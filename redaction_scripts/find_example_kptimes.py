# Exemple KPTimes

from glob import glob
import json
import os
import random

with open('data/datasets/KPTimes.test.jsonl') as f:
	f = map(json.loads, f)
	data = list(f)

kws = {}
for fp in glob('ake-benchmarking/output/KPTimes/*.json'):
	if 'stem' in fp:
		continue

	with open(fp) as f:
		tmp_content = json.load(f)
	key = os.path.basename(fp).split('.')[1]
	kws[key] = tmp_content

kws_keys = ['TfIdf', 'FirstPhrases', 'MultipartiteRank', 'Kea', 'CopyRNN', 'CopyRNN_News']


"""
Chapitre 4:

Un exemple de KPTimes qui montre la différence entre
les MC de CopySci et CopyNEws + méth chaînes
ny0110694
jp0006383


Un exemple de KP20k qui montre la différence entre
les MC de CopySci et CopyNews
"""


for i in random.sample(range(len(data)), 200):
	d = data[i]
	if d['abstract'].count(' ') < 500:
		continue
	print(d['title'], d['id'])
	print(d['abstract'])
	print(f'{"ref":<17}', d['keyword'].split(';'))
	for k in kws_keys:
		print(f'{k:<17}', [v for kws in kws[k][d['id']][:5] for v in kws])
	input()