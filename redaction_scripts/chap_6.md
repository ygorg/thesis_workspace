# Comparer les scores des requetes et ragarder la modification par RM3

Question: Pourquoi T+A+Corr est moins performant que T+A avec QL+RM3?
Hypothèse: c'est à cause de RM3 qui fait du topic drifting à cause des mots-clés de CorrRNN.

Donc ce que je veux trouver c'est que les termes ajouté à la requete grâce à RM3 apparaissent dans des documents non pertinent.
Ca veut dire que les termes ajouté par RM3 sans que les document soient supplémentés sont "meilleurs" que les termes ajoutés avec des doc supplémentés.

1. Trouver une requête
2. Trouver les termes ajouté par RM3
3. Trouver les documents non pertinent


## Regarder la différence de score des requêtes

Quelle requête à eu un grand changement de score ? pour 1 modèle avec et sans MC prédit.
La 131

```python
def load_scores(p):
    data = {}
    with open(p) as f:
        for l in f:
            metric, qid, sc = l.strip().split('\t')
            if metric.strip() == 'recall_1000':
                continue
            data[qid] = float(sc)
    return data


COLLECTION="ntcir-2"
TOPICFIELD="description"
MODEL="qld+rm3"
sc_ta = load_scores(f"data/{COLLECTION}/output/run.{COLLECTION}-t+a.description.{MODEL}.results")
sc_co = load_scores(f"data/{COLLECTION}/output/run.{COLLECTION}-t+a-CorrRNN.description.{MODEL}.results")
diff = sorted([(round(v-sc_ta[k], 3), round(v, 3), round(sc_ta[k], 3), k) for k, v in sc_co.items()])

print(diff[0], diff[-1])
#'146' +0.198
#'131' -0.188
```

## Afficher le rangs des documents pertinents

```bash
COLLECTION="ntcir-2"
TOPICFIELD="description"
MODEL="qld+rm3"
EXP="${COLLECTION}-t+a"
cat ${COLLECTION}/output/run.${EXP}.${TOPICFIELD}.${MODEL}.txt | cut -d' ' -f1,3,4,5 | grep -f <(cat ${COLLECTION}/qrels/rel1_ntc2-e2_0101-0149.qrels | grep '  1' | cut -f1,3 --output-delimiter=' ') | less

EXP="${COLLECTION}-t+a-CorrRNN"
cat ${COLLECTION}/output/run.${EXP}.${TOPICFIELD}.${MODEL}.txt | cut -d' ' -f1,3,4,5 | grep -f <(cat ${COLLECTION}/qrels/rel1_ntc2-e2_0101-0149.qrels | grep '  1' | cut -f1,3 --output-delimiter=' ') | less
```

Quels mots contiennent les document pertinent et pas pertinent ?

```python
from collections import defaultdict

COLLECTION="ntcir-2"
TOPICFIELD="description"
MODEL="qld+rm3"
REQ = '131'


def load_qrel(p):
    data = defaultdict(list)
    with open(p) as f:
        for l in f:
            qi, _, qd, r = l.strip().split('\t')
            if r == '0':
                continue
            data[qi].append(qd)
    return data


def load_res(p):
    data = defaultdict(dict)
    with open(p) as f:
        for l in f:
            qi, _, qd, r, s, _ = l.strip().split(' ')
            data[qi][qd] = int(r), float(s)
    return data


qrel = load_qrel(f'data/{COLLECTION}/qrels/rel1_ntc2-e2_0101-0149.qrels')
res_ta = load_res(f'data/{COLLECTION}/output/run.{COLLECTION}-t+a.{TOPICFIELD}.{MODEL}.txt')
res_co = load_res(f'data/{COLLECTION}/output/run.{COLLECTION}-t+a-CorrRNN.{TOPICFIELD}.{MODEL}.txt')

# Les documents de t+a qui sont pertinent
rel_id = [d for d in res_ta[REQ] if d in qrel[REQ]]
# Les doc qui sont remonté: les doc de CorrRNN avant le dernier doc pertinent
last_relevant_doc = max([res_co[REQ][d][1] for d in rel_id])
unrel_id = [k for k, v in res_co[REQ].items() if v[0] < last_relevant_doc and k not in rel_id]


# Différence de rang pour les doc pertinent et non pertinent
tmp = [res_ta[REQ][k][0] - res_co[REQ][k][0] for k in rel_id]
print(sum(tmp) / len(tmp))
tmp = [res_ta[REQ][k][0] - res_co[REQ][k][0] for k in unrel_id]
print(sum(tmp) / len(tmp))


with open('../data/datasets/NTCIR1+2.test.jsonl') as f:
    f = map(json.loads, f)
    data = {d['id']: d for d in f if d['id'] in rel_id + unrel_id}
for d in data.values():
    d['preproc'] = set(map(stem, nltk.word_tokenize(d['title'] + ' . ' + d['abstract'])))

# qu_ta = load_query(f"{COLLECTION}-t+a.{MODEL}.txt")
# req_ta = [e[0] for e in qu_ta[REQ][0] + qu_ta[REQ][1]]
req_ta = set(["evid", "exist", "field", "instanton", "other", "qcd", "quantum", "quark", "realli", "theori", "topolog", "what", "equat", "perturb", "supersymmetr"])
# qu_co = load_query(f"{COLLECTION}-t+a-CorrRNN.{MODEL}.txt")
# req_co = [e[0] for e in qu_co[REQ][0] + qu_co[REQ][1]]
req_co = set(["evid", "exist", "field", "instanton", "other", "qcd", "quantum", "quark", "realli", "theori", "topolog", "what", "group", "lattic", "string"])

# Différence du nb de mots commun à la requete pour les doc pertinent et non peritnent
tmp = [len(req_ta & data[k]['preproc']) - len(req_co & data[k]['preproc']) for k in rel_id]
print(sum(tmp) / len(tmp))
tmp = [len(req_ta & data[k]['preproc']) - len(req_co & data[k]['preproc']) for k in unrel_id]
print(sum(tmp) / len(tmp))
```

## Afficher les requete avant et après RM3

Quels sont les mots qui ont été ajouté à la requête ?

```bash
COLLECTION="ntcir-2"
TOPICFIELD="description"
MODEL="qld"

EXP="${COLLECTION}-t+a"
INDEX="data/${COLLECTION}/indexes/lucene-index.${EXP}"
sh anserini/target/appassembler/bin/SearchCollection \
   -topicreader Trec \
   -index ${INDEX} \
   -topics data/${COLLECTION}/topics/topic-e0101-0149.title+desc+narr.trec \
   -${MODEL} -rm3 -rm3.outputQuery \
   -topicfield ${TOPICFIELD} -output /dev/null | grep 'QID' -A 2 | sed 's/.* - //g' > ${EXP}.${MODEL}+rm3.txt 2>&1

EXP="${COLLECTION}-t+a-CorrRNN"
INDEX="data/${COLLECTION}/indexes/lucene-index.${EXP}"
sh anserini/target/appassembler/bin/SearchCollection \
   -topicreader Trec \
   -index ${INDEX} \
   -topics data/${COLLECTION}/topics/topic-e0101-0149.title+desc+narr.trec \
   -${MODEL} -rm3 -rm3.outputQuery \
   -topicfield ${TOPICFIELD} -output /dev/null | grep 'QID' -A 2 | sed 's/.* - //g' > ${EXP}.${MODEL}+rm3.txt 2>&1
```


## Regarder la modification de la requête
```python
def alignn(la, lb, k=(lambda x: x), def_e=''):
    kla = [k(x) for x in la]
    klb = [k(x) for x in lb]
    aa, bb = [], []
    for e in la:
        if k(e) in klb:
            aa += [e]
            bb += [e]
        else:
            aa += [e]
            bb += [def_e]
    for e in lb:
        if k(e) in kla:
            continue
        else:
            aa += [def_e]
            bb += [e]
    return [(a, b) for a, b in zip(aa, bb)]


def load_query(p):
    data = {}
    with open(p) as f:
        file = [l.strip() for l in f]
    i = 0
    while i < len(file):
        l = file[i]
        qid = l.split(' ')[-1]
        i += 1
        l = file[i]
        #old = [e.split('^')[0][1:-1] for e in l.split('uery: ')[1].split(' ')]
        old = [e.split('^') for e in l.split('uery: ')[1].split(' ')]
        old = [(w[1:-1], round(float(s)*100)) for w, s in old]
        old = sorted(old, key=lambda x: x[0])

        i += 1
        l = file[i]
        #new = [e.split('^')[0][1:-1] for e in l.split('uery: ')[1].split(' ')]
        new = [e.split('^') for e in l.split('uery: ')[1].split(' ')]
        new = [(w[1:-1], round(float(s)*100)) for w, s in new]
        new = sorted(new, key=lambda x: x[0])
        old_words = [p[0] for p in old]
        #new = sorted(enumerate(new), key=lambda i, x: old_words.index(x[0]) if x[0] in old_words else len(old_words) + i)
        new = sorted(new, reverse=True, key=lambda x: x[0] in old_words)
        #data[qid] = (old, [e for e in new if e[0] not in [o[1] for o in old]])
        data[qid] = (new[:len(old)], new[len(old):])

        i+=1
    return data

qu_ta = load_query("ntcir-2-t+a.qld+rm3.txt")
qu_co = load_query("ntcir-2-t+a-CorrRNN.qld+rm3.txt")
alignn(qu_ta['131'][1], qu_co['131'][1], k=lambda x: x[0], def_e=('', 0))
```

## Tableau ir_per_domain
```python
data = []
for meth in ['', '-MultipartiteRank', '-KeaOneModel', '-CorrRNN', '-CopyRNN']:
    acc = []
    for kps in ['', '-all']:
        for domain in [1, 2]:
            model = 'bm25'
            # The baseline is the same system but without predicted keywords
            baseline = load_scores(f'data/ntcir-2/output/run.ntcir-2-t+a{kps}.description.{model}.results')
            baseline = [v for k, v in baseline.items() if domains.get(k, []) == [domain]]
            baseline_score = sum(baseline) / len(baseline)

            system_ = load_scores(f'data/ntcir-2/output/run.ntcir-2-t+a{kps}{meth}.description.{model}.results')
            system_ = [v for k, v in system_.items() if domains.get(k, []) == [domain]]
            system_score = sum(system_) / len(system_)

            ttest = stats.ttest_rel(a=baseline, b=system_)[1]
            sign = ttest < .05

            diff_score = system_score - baseline_score

            tmp_d = 'I' if domain == 1 else 'O'
            tmp_k = 'tak' if kps[1:] else 'ta'
            data.append((meth[1:], tmp_k, tmp_d, system_score, diff_score, sign))

df = pd.DataFrame(data, columns=['m', 'k', 'd', 's', 'diff', 'sign'])
df['is_max'] = df.groupby(['k', 'd'])['s'].transform('max') == df['s']
df['print_s'] = df.apply(lambda x: stylee(round(x['s']*100, 1), x['sign'], x['is_max'], x['diff']) + (' ' +
                                   add_latex_command('ddiff', round(x['diff']*100, 1)) if round(x['diff'], 3) else ''), axis=1)

```

## Créer référence par domaine

```python
import json
from collections import defaultdict
ROOT='/home/gallina/'

with open(ROOT + '/ir-using-kg/data/topics/domains.json') as f:
    domains = json.load(f)

qrel = load_qrel(f'{ROOT}/redefining-absent-keyphrases/data/ntcir-2/qrels/rel1_ntc2-e2_0101-0149.qrels')

path_ake_datasets = ROOT + '/ake-datasets/datasets/'

with open(path_ake_datasets+'NTCIR1+2/references/test.indexer.stem.json') as f:
    ref = json.load(f)

in_domain_ref = {}
out_domain_ref = {}
for k in domains:
    if domains[k] == [1]:
        for doc_id in qrel[k]:
            if doc_id in ref:
                in_domain_ref[doc_id] = ref[doc_id]
    elif domains[k] == [2]:
        for doc_id in qrel[k]:
            if doc_id in ref:
                out_domain_ref[doc_id] = ref[doc_id]

with open(path_ake_datasets+'NTCIR1+2/references/test.indexer_in.stem.json', 'w') as f:
    json.dump(in_domain_ref, f)
with open(path_ake_datasets+'NTCIR1+2/references/test.indexer_out.stem.json', 'w') as f:
    json.dump(out_domain_ref, f)
```

```bash
cd /home/gallina/ake-benchmarking
for DOM in "in" "out"
do
    echo ${DOM}
    for METH in "MultipartiteRank" "CorrRNN" "CopyRNN"
    do
        python3 eval.py -n 5 -i "output/NTCIR1+2/NTCIR1+2.${METH}.stem.json" \
                             -r "../ake-datasets/datasets/NTCIR1+2/references/test.indexer_${DOM}.stem.json"
    done
done

rm /home/gallina/ake-datasets/datasets/NTCIR1+2/references/test.indexer_*.stem.json
```


## Load scores

```python
import os
import pandas as pd
from glob import glob
from scipy import stats


def load_scores(p):
    data = {}
    with open(p) as f:
        for l in f:
            metric, qid, sc = l.strip().split('\t')
            if metric.strip() == 'recall_1000':
                continue
            data[qid] = float(sc)
    return data


def mean(l):
    return sum(l) / len(l)


def param_to_file(coll, sys_, r, m, n, p):
        if m and not n or p and not m:
            raise ArgumentError()
        tmp = []
        if r:
            tmp += [r]
        if m:
            tmp += [m, n]
            if p:
                tmp += [p]
        if tmp:
            tmp = '-' + '-'.join(tmp)
        else:
            tmp = ''

        return f'../data/{coll}/output/run.{coll}-t+a{tmp}.description.{sys_}.results'


def file_to_param(f):
    coll = f.split(os.sep)[-3]
    exp, _, sys_ = os.path.basename(f).split('.')[1:4]
    exp_ = exp.split('-')[3:]
    if not exp_:
        exp_ = ['none'] * 4
    elif exp_[0][0].islower():
        # there are reference keyphrases
        exp_ += ['none'] * (4 - len(exp_))
    else:
        # there are reference keyphrases
        exp_ = ['none'] + exp_ + ['none'] * (3 - len(exp_))
    r, m, n, p = exp_
    return coll, sys_, r, m, n, p


def add_latex_command(command, value):
    return f'\\{command}{{{value}}}'


def stylee(v, sign, best, diff):
    com = ''
    if best:
        com = 'best'
        if sign:
            com += 's'
    elif sign:
        com = 'sign'

    if com:
        return_val = add_latex_command(com, v)
    else:
        return_val = f'{v}'

    if round(diff, 1):
        return_val += ' & ' + add_latex_command('ddiff', round(diff, 1))
    return return_val


files = glob('../data/ntcir-2/output/*.results')

data = []
for f in files:
    coll, sys_, r, m, n, p = file_to_param(f)
    s = load_scores(f)
    s.pop('all')
    mean_s = mean(s.values()) * 100

    s_baseline = load_scores(param_to_file(coll, sys_, None if r == 'none' else r, None, None, None))
    s_baseline.pop('all')
    mean_s_baseline = mean(s_baseline.values()) * 100

    tmp_keys = list(s_baseline)
    ttest = stats.ttest_rel(a=[s[k] for k in tmp_keys], b=[s_baseline[k] for k in tmp_keys])[1]
    sign = ttest < .05

    data.append([coll, r, m, n, p, sys_, mean_s, sign, mean_s - mean_s_baseline, f])

df = pd.DataFrame(data, columns=['collection', 'ref', 'method', 'n', 'prmu', 'system', 'score', 'sign', 'diff', 'file_path'])
```

## Tableau ir_results

```python
filtered_df = df[df['ref'].isin(['none', 'all'])]
table = filtered_df.groupby(['ref', 'method', 'system']).apply(lambda x: x.to_dict('records')[0]).apply(lambda x: stylee(round(x['score'], 1), x['sign'], False, x['diff']))
mean_table = filtered_df.groupby(['ref', 'method']).mean().round(1)[['score', 'diff']].apply(lambda x: stylee(x['score'], False, False, x['diff']), axis=1)
mean_table.name='mean'
table = pd.concat([table.unstack(), mean_table], axis=1)
table_str = table.reindex(['none', 'MultipartiteRank', 'KeaOneModel', 'CorrRNN', 'CopyRNN'], level=1).to_latex(escape=False)
table_str = table_str.replace('MultipartiteRank', 'MPRank').replace('bm25', '\\textsc{Bm25}').replace('qld', 'QL')\
                     .replace('rm3', 'RM3').replace('KeaOneModel', 'Kea (KP20k)')
print(table_str)
```

## Tableau ir_all-abs-pres

```python
filtered_df = df[df['system'] == 'bm25+rm3'][df['ref'].isin(['none', 'all'])][df['method'].isin(['CopyRNN', 'none', 'CorrRNN'])][df['n'].isin(['5', 'none'])][df['prmu'].isin(['rmu', 'p', 'none'])]
table = filtered_df.groupby(['ref', 'prmu', 'method']).apply(lambda x: x.to_dict('records')[0]).apply(lambda x: stylee(round(x['score'], 1), x['sign'], False, 0))
print(table.reindex(['none', 'CopyRNN', 'CorrRNN'], level=2).reindex(['none', 'all'], level=0).unstack(0).unstack(0).to_latex(escape=False))
```

## Tableau full_retrieval_results

```python
df[df['system'].isin(['bm25', 'bm25+rm3'])][df['method'] == 'none'].groupby(['collection', 'ref', 'system'])['score'].min().unstack(0).unstack(1).reindex(['none', 'p', 'r', 'm', 'u', 'rmu', 'pr', 'mu', 'all']).round(1)
```

## Figure n_vs_perf

```python
for ref in ['all', 'none']:
    filtered_df = df[df['system'] == 'bm25+rm3'][df['ref'] == ref][df['method'].isin(['CopyRNN', 'CorrRNN', 'MultipartiteRank', 'KeaOneModel'])][df['prmu'] == 'none']

    baseline = df[df['system'] == 'bm25+rm3'][df['ref'] == ref][df['method'] == 'none']
    if len(baseline) == 1:
        baseline = baseline['score'].values[0]

    print("""
    \\begin{subfigure}{\\textwidth}
    \\centering
    \\begin{tikzpicture}[trim axis left,trim axis right]""")
    if ref == 'none':
        print("""
    \\begin{axis}[
        width=0.7\\textwidth,
        height=5cm,
        ymin=31.5,ymax=35.0,
        xmin=-1,xmax=10,
        xtick = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9},
        xticklabels={$N$=0\\quad~~,1, 2, 3, 4, 5, 6, 7, 8, 9},
        ytick = {32, 33, 34},
        tick pos=left,
        grid style={dashed, gray!50},
        xmajorgrids,
        ]
    \\node[] at (axis cs: .4, 37.5) {{{{\\small \\tr}}}};""")
    else:
        print("""
    \\begin{axis}[
        width=0.7\\textwidth, height=5cm,
        ymin=34.5, ymax=38,
        xmin=-1, xmax=10,
        xtick = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9},
        xticklabels={,,,},
        ytick = {35, 36, 37},
        tick pos=left,
        grid style={dashed, gray!50},
        xmajorgrids,
        legend style={font=\\small,anchor=north east, draw=none, fill=none}
        ]
    \\node[] at (axis cs: .4, 37.5) {{{{\\small \\trm}}}};""")

    sign = []
    for m, rows in filtered_df.groupby(['method'])[['n', 'score']]:
        rows = rows.sort_values('n')
        rows = rows[['n', 'score', 'sign']].to_dict('split')['data']
        for n, v, s in rows:
            if s:
                sign.append((n, v))

        print(f"""
        \\addplot+[smooth] plot coordinates {{
            {' '.join([f'({n}, {v:.2f})' for n, v, s in rows])}}};
        \\addlegendentry{{{m}}}\n""")

    print(f"""
    % baseline
    \\addplot[mark=none, black, dashed] coordinates {{(0, {baseline}) (9, {baseline})}};

    % significative points
    \\addplot[only marks, mark=square, color=black, thick, mark size=3pt] plot coordinates {{
        {' '.join([f'({n}, {v:.2f})' for n, v in sign])}}};

    \\end{{axis}}
    \\end{{tikzpicture}}
    \\end{{subfigure}}\n""")
    input()
```