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


def param_to_file(coll, sys_, r, m, n, p, out):
    if m and not n or p and not m:
        raise ArgumentError()
    n = str(n)
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

    if out == 'req':
        return f'/home/gallina/redefining-absent-keyphrases/data/{coll}/output/run.{coll}-t+a{tmp}.description.{sys_}.req'
    elif out == 'res':
        return f'/home/gallina/redefining-absent-keyphrases/data/{coll}/output/run.{coll}-t+a{tmp}.description.{sys_}.results'
    elif out == 'txt':
        return f'/home/gallina/redefining-absent-keyphrases/data/{coll}/output/run.{coll}-t+a{tmp}.description.{sys_}.txt'
    elif out == None:
        return f'/home/gallina/redefining-absent-keyphrases/data/{coll}/output/run.{coll}-t+a{tmp}.description.{sys_}'
    elif out == 'col':
        return glob(f'/home/gallina/redefining-absent-keyphrases/data/{coll}/collections/{coll}-t+a{tmp}/*.gz')[0]
    

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

path_a = param_to_file(COLLECTION, MODEL, None, 'CopyRNN', 5 ,None)
path_b = param_to_file(COLLECTION, MODEL, None, 'CorrRNN', 5 ,None)
sc_a, sc_b = load_scores(path_a), load_scores(path_b)
res_a, res_b = load_scores(path_a.replace('.results', '.txt')), load_scores(path_b.replace('.results', '.txt'))

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
qrel = load_qrel(f'data/ntcir-2/qrels/rel1_ntc2-e2_0101-0149.qrels')
with open('data/ntcir-2/topics/topic-e0101-0149.title+desc+narr.trec') as f:
    query_data = f.read().split()

path_clean = param_to_file('ntcir-2', 'bm25+rm3', None, None, None ,None, out=None)
path_kw = param_to_file('ntcir-2', 'bm25+rm3', None, 'CopyRNN', 5 ,None, out=None)
path_col_clean = param_to_file('ntcir-2', 'bm25+rm3', None, None, None ,None, out='col')
path_col_kw = param_to_file('ntcir-2', 'bm25+rm3', None, 'CopyRNN', 5 ,None, out='col')

with gzip.open(path_col_kw) as f:
    doc_data = f.read().split()

# Je cherche une requête qui baisse quand on ajoute des mots-clés.
sc_clean, sc_kw = load_scores(path_clean + '.results'), load_scores(path_kw + '.results')
diff = sorted([(round(sc_kw[req] - sc_clean[req], 3), round(sc_kw[req], 3), round(sc_clean[req], 3), k) for req in sc_clean])
print(diff[:-4])

# Je cherche si les termes ajoutés ont un rapport avec la requête
qu_kw = load_query(path_kw + '.req')
for _, _, _, req in diff[-4]:
    # Pour chaque requête la requête et le RM3
    idx = query_data.index(f'<num> Number: {req}\n')
    print(''.join(query_data[idx:idx+7]))
    print(qu_kw[REQ])
    input()

# Quels sont les 10 documents qui ont servis a étendre la requête ?
res_kw_norm = load_res(path_kw.replace('+rm3', '') + '.txt')
for _, _, _, req in diff[:-4]:
    first_docs = [d for d, (r, v) in res_kw_norm[req].items() if r < 10]
    nb_rel = len(d for d in first_docs if d in qrel[req])
    print(f'{nb_rel / len(first_docs) * 100:.1f}% relevant')
    for d in first_docs:
        # là il faut afficher les mots-clés
        # est-ce que les mots-clés sont dans les termmes ajoutés par RM3 ?
        # est-ce que les mots-clés sont pertinent pour le document
        idx = doc_data.index(f'<DOCNO>{d}</DOCNO>\n')
        print(doc_data[idx:idx+10])
        input()
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
