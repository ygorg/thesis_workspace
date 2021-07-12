import json
import glob
from collections import Counter

from tqdm import tqdm
import matplotlib.pyplot as plt

key_freq = {}
freq_distrib = {}

for path in tqdm(glob.glob('ake-datasets/datasets/*/references/*test*.json')):
    with open(path) as f:
        r = json.load(f)
    key = '/'.join(path.split('/')[2:5:2])
    key = key.replace('.json', '').replace('test.', '')
    key_freq[key] = Counter(v for d in r.values() for k in d for v in k)
freq_distrib = {k: Counter(v.values()) for k, v in key_freq.items()}

for k, v in freq_distrib.items()
    nb_values = sum(f for c, f in v.items())
    # en moyenne cb de fois 1 mc apparait ??
    a = sum(c * f for c, f in v.items()) / nb_values
    # c'est quoi le max ?
    b = max(c for c, f in v.items())
    print(k, a, b)


freq_distrib = {
    k: [v[i] / sum(v.values()) * 100 for i in range(1, 6)]
    for k, v in freq_distrib.items()}
to_filter_out = ['NYTime', 'abstract', 'test55', 'RefSee']
freq_distrib = {
    k: v for k, v in freq_distrib.items()
    if 'stem' in k and all(d not in k for d in to_filter_out)
}


full = 'CSTR NUS PubMed ACM Citeulike-180 SemEval-2010'.split()
abstract = 'Inspec KDD WWW TermITH-Eval KP20k NTCIR1+2 TALN-Archives'.split()
news = 'DUC-2001 110-PT-BN-KP 500N-KPCrowd WikinewsKeyphrase KPTimes'.split()

fig, ax = plt.subplots(1, 3, sharey=True)
for i, corp_names in enumerate([full, abstract, news]):
    for k, v in freq_distrib.items():
        if not any(c in k for c in corp_names):
            continue
        ax.flat[i].plot(range(1, len(v) + 1), v, label=k)
    ax.flat[i].legend()
plt.tight_layout()
plt.show()
