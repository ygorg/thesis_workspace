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
from typing import Dict, List, Tuple
from collections import defaultdict
from glob import glob
import gzip


def exp_to_param(exp):
    """{coll}-t+a{tmp}"""
    exp_ = exp.split('-')[3:]
    if not exp_:
        exp_ = [None] * 4
    elif exp_[0][0].islower():
        # there are reference keyphrases
        exp_ += [None] * (4 - len(exp_))
    else:
        # there are reference keyphrases
        exp_ = [None] + exp_ + [None] * (3 - len(exp_))
    return exp_


def file_to_param(f):
    """/home/gallina/redefining-absent-keyphrases/data/{coll}/output/run.{coll}-t+a{tmp}.description.{sys_}.results"""
    coll = f.split(os.sep)[-3]
    exp, _, sys_ = os.path.basename(f).split('.')[1:4]
    r, m, n, p = exp_to_param(exp)
    return coll, sys_, r, m, n, p


def param_to_file(coll, sys_, r, m, n, p, out):
    if m and not n or p and not m:
        raise ArgumentError()
    if n is not None:
        n = str(n)
    tmp = list(filter(None, [r, m, n, p]))
    if tmp:
        tmp = '-' + '-'.join(tmp)
    else:
        tmp = ''

    exp_ = f'{coll}-t+a{tmp}'
    home_ = '/home/gallina/redefining-absent-keyphrases'
    output_ = f'{home_}/data/{coll}/output/run.{exp_}.description.{sys_}'

    out_dict = {'req': output_+'.req',
     None: output_,
     'res': output_ + '.results',
     'txt': output_ + '.txt',
     'col': glob(f'{home_}/data/{coll}/collections/{exp_}/*.gz')[0]
    }
    return out_dict[out]
    

def load_scores(p) -> Dict[str, float]:
    data = {}
    with open(p) as f:
        for l in f:
            metric, qid, sc = l.strip().split('\t')
            if metric.strip() == 'recall_1000':
                continue
            data[qid] = float(sc)
    return data


def load_qrel(p) -> Dict[str, List[str]]:
    data = defaultdict(list)
    with open(p) as f:
        for l in f:
            qi, _, qd, r = l.strip().split('\t')
            if r == '0':
                continue
            data[qi].append(qd)
    return data


def load_res(p) -> Dict[str,Dict[str,Tuple[int, float]]]:
    data = defaultdict(dict)
    with open(p) as f:
        for l in f:
            qi, _, qd, r, s, _ = l.strip().split(' ')
            data[qi][qd] = int(r), float(s)
    return data

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


COLLECTION="ntcir-2"
MODEL="bm25+rm3"
REQ = '131'

qrel = load_qrel(f'data/ntcir-2/qrels/rel1_ntc2-e2_0101-0149.qrels')

path_a = param_to_file(COLLECTION, MODEL, 'all', None, None ,None, 'res')
path_b = param_to_file(COLLECTION, MODEL, 'all', 'CorrRNN', 5 ,None, 'res')
sc_a, sc_b = load_scores(path_a), load_scores(path_b)
res_a, res_b = load_res(path_a.replace('.results', '.txt')), load_res(path_b.replace('.results', '.txt'))

# Différence de score entre les requêtes
diff = sorted([(round(v-sc_b[k], 3), round(v, 3), round(sc_b[k], 3), k) for k, v in sc_a.items()])
print(diff[0], diff[-2])


# Rangs des documents pertinents
[r for d, (r, v) in res_a[REQ].items() if d in qrel[REQ]]


# Documents pertinent de la requête
rel_id = [d for d in res_a[REQ] if d in qrel[REQ]]
# Les doc qui sont remonté: les doc de CorrRNN avant le dernier doc pertinent
last_relevant_doc = max([res_b[REQ][d][1] for d in rel_id])
unrel_id = [k for k, v in res_b[REQ].items() if v[0] < last_relevant_doc and k not in rel_id]

tmp = [res_a[REQ][k][0] - res_b[REQ][k][0] for k in rel_id]
print(sum(tmp) / len(tmp))
tmp = [res_a[REQ][k][0] - res_b[REQ][k][0] for k in unrel_id]
print(sum(tmp) / len(tmp))

```

OK le vrai test est ici:
```python

## Trouver une requête qui baisse
# 1. Quelle est la requête qui baisse le plus dans toutes les expériences ?
diff = []
for path in glob('data/ntcir-2/output/*.results'):
    a = load_scores(path)
    coll, sys_, r, m, n, p = file_to_param(path)
    b = load_scores(param_to_file(coll, sys_, r if r != 'none' else None, None, None, None, out='res'))
    diff += [(path, round(a[req] - b[req], 3), round(a[req], 3), round(b[req], 3), req) for req in a]
diff = sorted(diff, key=lambda x: x[1])

# og_path = 'data/ntcir-2/output/run.ntcir-2-t+a-all-CorrRNN-5.description.qld+rm3.results'

og_path = 'data/ntcir-2/output/run.ntcir-2-t+a-CopyRNN-5-mu.description.bm25+rm3.results'
coll, sys_, ref, meth, top_n, prmu = file_to_param(og_path)
path_clean = param_to_file(coll, sys_, ref, None, None ,None, out=None)
path_kw = param_to_file(coll, sys_, ref, meth, top_n ,prmu, out=None)

req = '146'

# 2. Je cherche une requête qui baisse quand on ajoute des mots-clés.
og_path = 'data/ntcir-2/output/run.ntcir-2-t+a-CopyRNN-5-mu.description.bm25+rm3.results'
og_path = 'data/ntcir-2/output/run.ntcir-2-t+a-all-MultipartiteRank-1.description.bm25+rm3.results'
og_path = 'data/ntcir-2/output/run.ntcir-2-t+a-all-CorrRNN-1.description.bm25+rm3.results'
coll, sys_, ref, meth, top_n, prmu = file_to_param(og_path)
path_clean = param_to_file(coll, sys_, ref, None, None ,None, out=None)
path_kw = param_to_file(coll, sys_, ref, meth, top_n ,prmu, out=None)

sc_clean, sc_kw = load_scores(path_clean + '.results'), load_scores(path_kw + '.results')
diff = sorted([(round(sc_kw[req]*100 - sc_clean[req]*100, 1), round(sc_kw[req]*100, 1), round(sc_clean[req]*100, 1), req) for req in sc_clean])
req = diff[0][-1]

## Regarder les termes ajoutés par RM3

with open('data/ntcir-2/topics/topic-e0101-0149.title+desc+narr.trec') as f:
    query_data = f.read().split('\n')
idx = query_data.index(f'<num> Number: {req}')
print('\n'.join(query_data[idx:idx+8]))

qu_kw = load_query(path_kw + '.req')
print([e[0] for e in qu_kw[req][0]])
print([e[0] for e in qu_kw[req][1]])
input()



req = '146'
og_path = 'data/ntcir-2/output/run.ntcir-2-t+a-all-CorrRNN-5.description.qld+rm3.results'
coll, sys_, ref, meth, top_n, prmu = file_to_param(og_path)
path_clean = param_to_file(coll, sys_, ref, None, None ,None, out=None)
path_kw = param_to_file(coll, sys_, ref, meth, top_n ,prmu, out=None)
## Regarder les documents utilisé par RM3

path_col_kw = param_to_file(coll, sys_, ref, meth, top_n ,prmu, out='col')
with gzip.open(path_col_kw, 'rt') as f:
    doc_data = f.read().split('\n')

qrel = load_qrel(f'data/ntcir-2/qrels/rel1_ntc2-e2_0101-0149.qrels')
res_kw_norm = load_res(path_kw.replace('+rm3', '') + '.txt')
first_docs = sorted(res_kw_norm[req], key=lambda x: res_kw_norm[req][x][0])[:10]

nb_rel = sum(1 for d in first_docs if d in qrel[req])
print(f'{nb_rel / len(first_docs) * 100:.1f}% relevant')

kws_first_docs = []
for d in first_docs:
    idx = doc_data.index(f'<DOCNO>{d}</DOCNO>')
    title = doc_data[idx+1][7:-8]
    abstract = doc_data[idx+2][6:-7]
    kw_ref = doc_data[idx+3][6:-7].lower().split(' // ')
    kw_pred = doc_data[idx+4][6:-7].lower().split(' // ')
    kws_first_docs.append([title, abstract, kw_ref, kw_pred])
    #print('\n'.join([title, kw_ref, kw_pred]))
    #input()


# Si je n'ajoute pas de mots-clés: quel sont les termes ajotués grâce à RM3 ?
# Je cherche si les termes ajoutés ont un rapport avec la requête
qu_clean = load_query(path_clean + '.req')
# Pour chaque requête la requête et le RM3
idx = query_data.index(f'<num> Number: {req}')
print('\n'.join(query_data[idx:idx+8]))
print([e[0] for e in qu_clean[req][0]])
print([e[0] for e in qu_clean[req][1]])
input()

# Quels sont les 10 documents qui ont servis a étendre cette requête ?
res_clean_norm = load_res(path_clean.replace('+rm3', '') + '.txt')
first_docs = [d for d, (r, v) in res_clean_norm[req].items() if r <= 10]
nb_rel = sum(1 for d in first_docs if d in qrel[req])
print(f'{nb_rel / len(first_docs) * 100:.1f}% relevant')
clean_first_docs = []
for d in first_docs:
    # est-ce que les mots-clés sont dans les termes ajoutés par RM3 ?
    # est-ce que les mots-clés sont pertinent pour le document
    idx = doc_data.index(f'<DOCNO>{d}</DOCNO>')
    title = doc_data[idx+1][7:-8]
    abstract = doc_data[idx+2][6:-7]
    kw_ref = doc_data[idx+3][6:-7].lower().split(' // ')
    clean_first_docs.append([title, abstract, kw_ref, []])

```


Quels mots contiennent les document pertinent et pas pertinent ?

```python

qrel = load_qrel(f'data/{COLLECTION}/qrels/rel1_ntc2-e2_0101-0149.qrels')
res_a = load_res(param_to_file(COLLECTION, MODEL, None, 'CopyRNN', 5 ,None).replace('.results', '.txt'))
res_b = load_res(param_to_file(COLLECTION, MODEL, None, 'CorrRNN', 5 ,None).replace('.results', '.txt'))

# Les documents de t+a qui sont pertinent
rel_id = [d for d in res_a[REQ] if d in qrel[REQ]]
# Les doc qui sont remonté: les doc de CorrRNN avant le dernier doc pertinent
last_relevant_doc = max([res_b[REQ][d][1] for d in rel_id])
unrel_id = [k for k, v in res_b[REQ].items() if v[0] < last_relevant_doc and k not in rel_id]


# Différence de rang pour les doc pertinent et non pertinent
tmp = [res_a[REQ][k][0] - res_b[REQ][k][0] for k in rel_id]
print(sum(tmp) / len(tmp))
tmp = [res_a[REQ][k][0] - res_b[REQ][k][0] for k in unrel_id]
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
