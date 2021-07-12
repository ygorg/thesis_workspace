# Weakly supervised keyphrase generation

## Ideas

- Perform context categorization to select only the most relevant contexts


## Todo with unarXive

[x] Create usable id: context data. Selection of contexts which cited paper is in arxiv. (arxiv_cited_id != None)
	- `python3 src/extract-citation-contexts.py data/unarXive-2020/contexts/extracted_contexts.csv > data/in_arxiv_contexts.json`
[x] Match cited ids with title and abstract
```python
# Using kaggle_metadata
import json
# Load contexts
with open('data/in_arxiv_contexts.json') as f:
	contexts = json.load(f)
	# 608469 keys

# Load kaggle metadata
with open('data/arxiv_kaggle/arxiv-metadata-oai-snapshot.json') as f:
	f = map(json.loads, tqdm(f, total=1890031))
	metadata = [l for l in f if l['id'] in contexts]  # 466110
# Filter out unnecessary infos
to_keep =  ['id', 'title', 'abstract', 'update_date', 'categories', 'doi']
metadata = [{k: l[k] for k in to_keep} for l in metadata]
# Add contexts
[l.update({'context': contexts[l['id']]}) for l in metadata]
with open('data/data_with_context.jsonl', 'w') as f: 
	for l in metadata: 
		f.write(json.dumps(l) + '\n') 
# Retrieving original
# import tarfile
# with open('data/in_arxiv_contexts.json') as f:
# 	contexts = json.load(f)
# f = tarfile.open('data/unarxive/unarXive-2020.tar.bz2', 'r:bz2')
# for id_ in contexts:
# 	doc = f.extractfile(f'unarXive-2020/papers/{id_}.txt')
# 	doc = doc.read().decode('utf-8')
# 	find title and abstract ????
```
[x] Match titles with other datasets (to find author keyphrases)
```python
import re
import json
from tqdm import tqdm
import string

punct_tab = str.maketrans(dict.fromkeys(string.punctuation))
for c in '\t\n \r':  # add whitespace characters
    punct_tab[ord(c)] = None


def preproc(title):
    return title.strip().lower().translate(punct_tab)


# `jsonl` files with ['id', 'title', 'keyword']
dataset_files = [
    'KP20k.test.jsonl', 'KP20k/full/kp20k.valid.json', 'ACM-abstract.test.jsonl',
    'tmp/Inspec.test.jsonl', 'tmp/Inspec.dev.jsonl', 'tmp/Inspec.train.jsonl', 'KDD.test.jsonl',
    'tmp/PubMed-titles.test.jsonl', 'SemEval-2010-abstract.test.jsonl', 'WWW.test.jsonl', 'tmp/acm-dl.test.jsonl',
    'KP20k/full/kp20k.train.json', 'NTCIR1+2.test.jsonl'
]

# Build a Dict[title,Tuple[info]]
title_mapping = {}
for path in dataset_files:
    with open('../data/datasets/' + path) as g:
        # Load the data
        g = map(json.loads, g)
        # Filter out doc w/o keywords
        g = filter(lambda x: 'keyword' in x, g)
        # Only keep id, title, keywords
        # And preprocess the titles to increase matching
        g = map(lambda d: (d['id'], d['title'], preproc(d['title']), d['keyword']), g)
        for id_, og_title, pr_title, k in g:
            # Fill the dict
            if pr_title in title_mapping:
                title_mapping[pr_title].append((id_, og_title, path, k))
            else:
                title_mapping[pr_title] = [(id_, og_title, path, k)]

# Choose mapping from acm-dl if exists else with the least kw
# (annnotation with the most keyword doesn't seem to match author keyphrases)
mapping_kws = {}
for k, v in title_mapping.items(): 
    matches = sorted(v, key=lambda x: ('acm-dl' in x[2], x[3].count(';')), reverse=True)
    mapping_kws[k] = matches[0][3]


with open('data/data_with_context.jsonl') as f:
	data = list(map(json.loads, f))

mapping = {d['id']: mapping_kws.get(preproc(d['title']), None) for d in data}
mapping = {k: v for k, v in mapping.items() if v}  # 6134
[d.update({'author_keyword': mapping[d['id']]}) for d in data if d['id'] in mapping]
with open('data/data_with_context_autkw.jsonl', 'w') as f: 
	for d in data: 
		f.write(json.dumps(d) + '\n')
```
[ ] Extract keyphrases from contexts
	- refseerx: select nounphrases adn then based on DF (number of context in which it appears) take the 10 best
	- this process is based on two steps:
		- select candidates in context
		- rank candidates from diff contexts

		- or what I can do is concat all contexts 
```python
import json
with open('data/data_with_context_autkw.jsonl') as f:
	data = list(map(json.loads, f))
```


Citation Classification using [Scicite](https://github.com/allenai/scicite)

```python
# allennlp predict scicite.tar.gz test.jsonl --predictor predictor_scicite --include-package scicite --overrides "{'model':{'data_format':''}}"
import json
o = open('contexts_for_classification.jsonl', 'w')
with open('data_with_context_autkw.jsonl') as f:
    f = map(json.loads, f)
    for l in f:
        for i, c in enumerate(l['context']):
            sample = {'string': c[1].replace('MAINCIT', '').replace('CIT', '').replace('FORMULA', ''), 'citingPaperId': c[0], 'citedPaperId': l['id'], 'excerpt_index': i, 'label': None, 'sectionName': None}
            o.write(json.dumps(sample) + '\n')
```