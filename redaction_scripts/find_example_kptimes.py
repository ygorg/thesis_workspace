# Exemple KPTimes

from glob import glob
import json
import os
import random

dataset = 'DUC-2001'

with open(f'data/datasets/dirty_jsonl/{dataset}.test.jsonl') as f:
    f = map(json.loads, f)
    data = list(f)

kws = {}
for fp in glob(f'ake-benchmarking/output/{dataset}/*.json'):
    #if 'stem' in fp:
    #   continue

    with open(fp) as f:
        tmp_content = json.load(f)
    key = os.path.basename(fp).split('.')[1]
    kws[key] = tmp_content

#kws_keys = ['TfIdf', 'FirstPhrases', 'MultipartiteRank', 'Kea', 'CopyRNN', 'CopyRNN_News']
kws_keys = ['TfIdf', 'Kea', 'CopyRNN_News']



WSJ910304-0002
FT934-11014

"""
Chapitre 4:

Un exemple de KPTimes qui montre la différence entre
les MC de CopySci et CopyNEws + méth chaînes
['ny0110694', 'jp0006383', 'ny0228890', 'jp0003769', 'jp0008484', 'jp0008968']
l'exemple avec le pollen est trop long

Un exemple de KP20k qui montre la différence entre
les MC de CopySci et CopyNews
"""

annot = {}
for i in random.sample(range(len(data)), 50):
    d = data[i]
    if d['title'].count(' ') + d['abstract'].count(' ') > 200:
        continue
    print(d['title'], d['id'])
    print(d['abstract'])
    print(f'{"ref":<17}', d['keyword'].split(';'))
    for k in kws_keys:
        print(f'{k:<17}', [v for kws in kws[k][d['id']][:5] for v in kws])
    label = input()
    annot[d['id']] = label