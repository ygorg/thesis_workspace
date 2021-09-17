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
cat ${COLLECTION}/output/run.${EXP}.${TOPICFIELD}.${MODEL}.txt | cut -d' ' -f1,3,4,5 | grep -f <(cat ${COLLECTION}/qrels/rel1_ntc2-e2_0101-0149.qrels | grep '	1' | cut -f1,3 --output-delimiter=' ') | less

EXP="${COLLECTION}-t+a-CorrRNN"
cat ${COLLECTION}/output/run.${EXP}.${TOPICFIELD}.${MODEL}.txt | cut -d' ' -f1,3,4,5 | grep -f <(cat ${COLLECTION}/qrels/rel1_ntc2-e2_0101-0149.qrels | grep '	1' | cut -f1,3 --output-delimiter=' ') | less
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



## Tableau full_retrieval_results

```python
import pandas as pd
data = []

# refaire avec for glob(output/*)
# et calculer la significativté avec la version sans mots-clés prédits

for c in ['acm-cr', 'ntcir-2']:
	with open(c + '.log') as f:
		for line in f:
			run_str, metric, score, sign, _ = line.strip().split('\t')

			_, run_name, _, ri_sys, _ = run_str.replace('ntcir-2', 'ntcir2').replace('acm-cr', 'acmcr').split('.')
			if run_name.count('-') == 2:
				cand_k = run_name.rsplit('-', 1)[-1]
				if any(k == cand_k for k in 'p r m u rmu pr mu all'.split(' ')):
					coll, _, ka = run_name.split('-')
					kg = ''
				else:
					coll, _, kg = run_name.split('-')
					ka = ''
			else:
				if run_name.count('-') == 1:
					run_name += '--'
				coll, _, ka, kg = run_name.split('-')

			data.append([coll, ka, kg, ri_sys, metric, float(score), sign])

df = pd.DataFrame(data, columns=['collection', 'kw', 'kwg', 'sys', 'metric', 'score', 'sign'])
df['kk'] = df.apply(lambda x: '-'.join(filter(None, [x['kw'], x['kwg']])), axis=1)

df[df['metric'] != 'recall_1000'][df['kw'].isin(['', 'all'])].groupby(['kw', 'kwg', 'collection', 'sys'])['score'].min().unstack(2).unstack().round(3)*100

# df[df['metric'] == 'recall_1000'][df['kw'].isin(['', 'all'])].groupby(['kw', 'kwg', 'collection', 'sys'])['score'].min().unstack(2).unstack().round(3)*100
```

## Tableau ir_per_domain
```python
from scipy import stats
print('      & \\multicolumn{2}{c}{T+A} & \\multicolumn{2}{c}{T+A+K} \\\\')
print('model &    I &    O &    I &    O \\\\')
for mod in ['', '-MultipartiteRank', '-KeaOneModel', '-CorrRNN', '-CopyRNN']:
	acc = []
	for kps in ['', '-all']:
		for domain in [1, 2]:

			# The baseline is the same system but without predicted keywords
			baseline = load_scores(f'data/ntcir-2/output/run.ntcir-2-t+a{kps}.description.bm25+rm3.results')
			baseline = [v for k, v in baseline.items() if domains.get(k, []) == [domain]]

			system_ = load_scores(f'data/ntcir-2/output/run.ntcir-2-t+a{kps}{mod}.description.bm25+rm3.results')
			system_ = [v for k, v in system_.items() if domains.get(k, []) == [domain]]

			ttest = stats.ttest_rel(a=baseline, b=system_)[1]
			sign = ttest < .05

			score = round(sum(system_) / len(system_) * 100, 1)
			score = str(score)
			if sign:
				score = f'\\sign{{{score}}}'

			acc.append(score)
	print(mod[1:] + ' & ' + ' & '.join(acc) + '\\\\')
```