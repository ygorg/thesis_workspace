# A TESTER
import json
import glob
from collections import Counter

import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt

key_freq = {}
freq_distrib = {}

to_filter_out = ['NYTime', 'c', 'abstract', 'test55', 'RefSee']
for path in tqdm(glob.glob('ake-datasets/datasets/*/references/*test*.json')):
    if 'stem' not in path or all(d not in path for d in to_filter_out):
        continue
    with open(path) as f:
        r = json.load(f)
    key = '/'.join(path.split('/')[2:5:2])
    key = key.replace('.json', '').replace('test.', '')
    key_freq[key] = Counter(v for d in r.values() for k in d for v in k)
    freq_distrib[key] = Counter(key_freq[key].values())




freq_distrib = {k: Counter(v.values()) for k, v in key_freq.items()}

ppp = []
for k, v in freq_distrib.items():
    nb_values = sum(f for c, f in v.items())
    # en moyenne cb de fois 1 mc apparait ??
    a = sum(c * f for c, f in v.items()) / nb_values
    # c'est quoi le max ?
    b = max(c for c, f in v.items())
    ppp.append((k, nb_values, round(a, 2), b))


# Quelle est de pourcentage de mots-clés associé X fois ?
freq_distrib = {
    k: [v[i] / sum(v.values()) * 100 for i in range(1, 6)]
    for k, v in freq_distrib.items()}

freq_distrib = {
   'KDD/author.stem': [78.6, 11.5, 3.6, 1.6, 1.1],
   'NUS/reader.stem': [92.1, 5.2, 1.6, 0.4, 0.4],
   'NUS/combined.stem': [90.7, 5.9, 1.4, 0.8, 0.5],
   'NUS/author.stem': [90.5, 6.2, 1.6, 0.8, 0.5],
   'WWW/combined.stem': [75.9, 12.2, 4.1, 2.1, 1.3],
   'WWW/author.stem': [77.5, 11.1, 3.8, 2.0, 1.4],
   'WWW/extra.stem': [88.0, 6.4, 2.3, 1.5, 0.5],
   'Inspec/uncontr.stem': [94.9, 3.9, 0.7, 0.2, 0.2],
   'Inspec/contr.stem': [58.7, 18.2, 8.2, 4.0, 3.1],
   'TALN-Archives/author.stem': [76.2, 11.7, 3.7, 2.5, 1.4],
   '500N-KPCrowd/reader.stem': [86.8, 9.0, 2.9, 1.0, 0.1],
   'CSTR/author.stem': [81.3, 11.5, 3.3, 1.7, 0.7],
   'PubMed/author.stem': [85.1, 9.3, 2.4, 1.2, 0.7],
   'Citeulike-180/reader.stem': [67.7, 13.9, 6.4, 3.5, 2.2],
   'WikinewsKeyphrase/reader.stem': [88.5, 8.2, 2.1, 0.9, 0.1],
   'DUC-2001/reader.stem': [82.1, 9.6, 4.2, 1.5, 0.8],
   'ACM/author.stem': [81.5, 10.2, 3.2, 1.9, 0.9],
   '110-PT-BN-KP/reader.stem': [84.9, 11.6, 3.0, 0.4, 0.0],
   'TermITH-Eval/indexer.stem': [68.2, 16.4, 5.4, 3.4, 1.9],
   'SemEval-2010/author.stem': [90.3, 6.8, 1.8, 0.6, 0.3],
   'SemEval-2010/combined.stem': [92.3, 5.3, 1.5, 0.4, 0.2],
   'SemEval-2010/reader.stem': [94.4, 4.3, 0.7, 0.3, 0.3],
   'NTCIR1+2/indexer.stem': [71.6, 12.1, 4.8, 2.6, 1.7],
   'KP20k/author.stem': [79.4, 10.2, 3.5, 1.8, 1.1],
   'KPTimes/editor.stem': [64.2, 12.3, 5.6, 3.2, 2.1]
}

df = pd.DataFrame(freq_distrib).T

full = 'CSTR NUS PubMed ACM Citeulike-180 SemEval-2010'.split()
abstract = 'Inspec KDD WWW TermITH-Eval KP20k NTCIR1+2 TALN-Archives'.split()
news = 'DUC-2001 110-PT-BN-KP 500N-KPCrowd WikinewsKeyphrase KPTimes'.split()


fig, ax = plt.subplots(1, 3, sharey=True)
for i, corp_names in enumerate([full, abstract, news]):
    for k, v in freq_distrib.items():
        if not any(c in k for c in corp_names):
            continue
        ax.flat[i].plot(range(1, len(v)+1), v, label=k)
    ax.flat[i].legend()
plt.tight_layout()
plt.show()