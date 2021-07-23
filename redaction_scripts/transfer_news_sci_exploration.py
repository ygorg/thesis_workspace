import json
from collections import Counter

import util


files = ["ake-benchmarking/output/KP20k/KP20k.CopyRNN.json",
"ake-benchmarking/output/KP20k/KP20k.CopyRNN_News.json",
"ake-benchmarking/output/KPTimes/KPTimes.CopyRNN.json",
"ake-benchmarking/output/KPTimes/KPTimes.CopyRNN_News.json"]

# Compute most producds keywords

for p in files:
    with open(p) as f:
        ref = json.load(f)
    c = Counter(v for d in ref.values() for k in d[:5] for v in k)
    print(p)
    print(c.most_common(10))

"""
KP20k CopyRNN.json
[('simulation', 469), ('design', 362), ('neural networks', 344), ('scheduling', 321), ('paper', 313), ('performance', 306), ('optimization', 289), ('classification', 284), ('data mining', 262), ('clustering', 245)]

KPTimes CopyRNN.json
[('’', 1236), ('japan', 1145), ('”', 937), ('“', 897), ('china', 866), ('trump', 500), ('russia', 431), ('police', 419), ('south korea', 320), ('north korea', 309)]

KP20k CopyRNN_News.json
[('computers and the internet', 8341), ('science and technology', 5741), ('research', 4653), ('tech industry', 2935), ('computer and video games', 2493), ('nyc', 2137), ('music', 1453), ('medicine and health', 1207), ('space', 1055), ('photography', 743)]

KPTimes CopyRNN_News.json
[('japan', 3556), ('donald trump', 1359), ('china', 1325), ('computers and the internet', 975), ('us foreign policy', 909), ('shinzo abe', 733), ('us politics', 631), ('international trade', 571), ('russia', 570), ('baseball', 534)]
"""

# Compute most produceds words

for p in files:
    with open(p) as f:
        ref = json.load(f)
    c = Counter(w for d in ref.values() for k in d[:5] for v in k for w in v.split(' '))
    print(p)
    print(c.most_common(10))


# Compute PRMU for each files

top_n = 5
res = []
for p in files:
    data_path = 'data/datasets/KPTimes.test.jsonl' if 'KPTimes' in p else 'data/datasets/KP20k.test.jsonl'
    p = '../' + p
    data_path = '../' + data_path

    for filt_str in 'prs_con prs_reo sem_prs abs_exc'.split(' '):
        data_stemmed = util.stem_data(data_path, n_thread=4)
        ref_path = util.filter_functions[filt_str](util.stemmed(p), data_stemmed, top_n=top_n)
        with open(p) as f:
            all_ref = json.load(f)
        with open(ref_path) as f:
            abs_ref = json.load(f)
        micro = sum(len(abs_ref[k][:top_n])/len(all_ref[k][:top_n]) for k in abs_ref)
        micro /= len(all_ref)
        res.append([p, 'KPTimes' if 'KPTimes' in p else 'KP20k', 'News' if '_News' in p else 'Sci', filt_str, micro * 100])
