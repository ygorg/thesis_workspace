import json
from collections import Counter
from itertools import combinations

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# title_mapping.json provient de ../citation-kpg/README.md
#  "Match titles with other datasets"

with open('title_mapping.json') as f:
    data = json.load(f)

data_dup = {k: v for k, v in data.items() if len(v) != 1}
nb_occ = Counter([d[-2] for v in list(data_dup.values()) for d in v])

ids = sorted(nb_occ)
mat = {k: {k: 0 for k in ids} for k in ids}
for a, b in [(a, b) for v in list(data_dup.values())[:10]
                    for a, b in combinations([d[-2] for d in v], 2)]:
    mat[a][b] += 1
    mat[b][a] += 1

mat = json.loads('{"ACM-abstract.test.jsonl":{"ACM-abstract.test.jsonl":0,"KDD.test.jsonl":11,"KP20k.test.jsonl":38,"KP20k\\/full\\/kp20k.train.json":1005,"KP20k\\/full\\/kp20k.valid.json":48,"NTCIR1+2.test.jsonl":5,"SemEval-2010-abstract.test.jsonl":0,"WWW.test.jsonl":7,"tmp\\/Inspec.dev.jsonl":3,"tmp\\/Inspec.test.jsonl":0,"tmp\\/Inspec.train.jsonl":6,"tmp\\/PubMed-titles.test.jsonl":0,"tmp\\/acm-dl.test.jsonl":279},"KDD.test.jsonl":{"ACM-abstract.test.jsonl":11,"KDD.test.jsonl":0,"KP20k.test.jsonl":22,"KP20k\\/full\\/kp20k.train.json":515,"KP20k\\/full\\/kp20k.valid.json":19,"NTCIR1+2.test.jsonl":0,"SemEval-2010-abstract.test.jsonl":0,"WWW.test.jsonl":0,"tmp\\/Inspec.dev.jsonl":0,"tmp\\/Inspec.test.jsonl":0,"tmp\\/Inspec.train.jsonl":0,"tmp\\/PubMed-titles.test.jsonl":0,"tmp\\/acm-dl.test.jsonl":676},"KP20k.test.jsonl":{"ACM-abstract.test.jsonl":38,"KDD.test.jsonl":22,"KP20k.test.jsonl":806,"KP20k\\/full\\/kp20k.train.json":1139,"KP20k\\/full\\/kp20k.valid.json":31,"NTCIR1+2.test.jsonl":2,"SemEval-2010-abstract.test.jsonl":3,"WWW.test.jsonl":33,"tmp\\/Inspec.dev.jsonl":3,"tmp\\/Inspec.test.jsonl":4,"tmp\\/Inspec.train.jsonl":7,"tmp\\/PubMed-titles.test.jsonl":2,"tmp\\/acm-dl.test.jsonl":734},"KP20k\\/full\\/kp20k.train.json":{"ACM-abstract.test.jsonl":1005,"KDD.test.jsonl":515,"KP20k.test.jsonl":1139,"KP20k\\/full\\/kp20k.train.json":28064,"KP20k\\/full\\/kp20k.valid.json":1102,"NTCIR1+2.test.jsonl":72,"SemEval-2010-abstract.test.jsonl":84,"WWW.test.jsonl":834,"tmp\\/Inspec.dev.jsonl":76,"tmp\\/Inspec.test.jsonl":59,"tmp\\/Inspec.train.jsonl":154,"tmp\\/PubMed-titles.test.jsonl":11,"tmp\\/acm-dl.test.jsonl":19539},"KP20k\\/full\\/kp20k.valid.json":{"ACM-abstract.test.jsonl":48,"KDD.test.jsonl":19,"KP20k.test.jsonl":31,"KP20k\\/full\\/kp20k.train.json":1102,"KP20k\\/full\\/kp20k.valid.json":798,"NTCIR1+2.test.jsonl":2,"SemEval-2010-abstract.test.jsonl":1,"WWW.test.jsonl":27,"tmp\\/Inspec.dev.jsonl":2,"tmp\\/Inspec.test.jsonl":2,"tmp\\/Inspec.train.jsonl":5,"tmp\\/PubMed-titles.test.jsonl":0,"tmp\\/acm-dl.test.jsonl":729},"NTCIR1+2.test.jsonl":{"ACM-abstract.test.jsonl":5,"KDD.test.jsonl":0,"KP20k.test.jsonl":2,"KP20k\\/full\\/kp20k.train.json":72,"KP20k\\/full\\/kp20k.valid.json":2,"NTCIR1+2.test.jsonl":8298,"SemEval-2010-abstract.test.jsonl":0,"WWW.test.jsonl":0,"tmp\\/Inspec.dev.jsonl":0,"tmp\\/Inspec.test.jsonl":1,"tmp\\/Inspec.train.jsonl":0,"tmp\\/PubMed-titles.test.jsonl":0,"tmp\\/acm-dl.test.jsonl":8},"SemEval-2010-abstract.test.jsonl":{"ACM-abstract.test.jsonl":0,"KDD.test.jsonl":0,"KP20k.test.jsonl":3,"KP20k\\/full\\/kp20k.train.json":84,"KP20k\\/full\\/kp20k.valid.json":1,"NTCIR1+2.test.jsonl":0,"SemEval-2010-abstract.test.jsonl":0,"WWW.test.jsonl":0,"tmp\\/Inspec.dev.jsonl":0,"tmp\\/Inspec.test.jsonl":0,"tmp\\/Inspec.train.jsonl":0,"tmp\\/PubMed-titles.test.jsonl":0,"tmp\\/acm-dl.test.jsonl":26},"WWW.test.jsonl":{"ACM-abstract.test.jsonl":7,"KDD.test.jsonl":0,"KP20k.test.jsonl":33,"KP20k\\/full\\/kp20k.train.json":834,"KP20k\\/full\\/kp20k.valid.json":27,"NTCIR1+2.test.jsonl":0,"SemEval-2010-abstract.test.jsonl":0,"WWW.test.jsonl":0,"tmp\\/Inspec.dev.jsonl":0,"tmp\\/Inspec.test.jsonl":0,"tmp\\/Inspec.train.jsonl":0,"tmp\\/PubMed-titles.test.jsonl":0,"tmp\\/acm-dl.test.jsonl":1237},"tmp\\/Inspec.dev.jsonl":{"ACM-abstract.test.jsonl":3,"KDD.test.jsonl":0,"KP20k.test.jsonl":3,"KP20k\\/full\\/kp20k.train.json":76,"KP20k\\/full\\/kp20k.valid.json":2,"NTCIR1+2.test.jsonl":0,"SemEval-2010-abstract.test.jsonl":0,"WWW.test.jsonl":0,"tmp\\/Inspec.dev.jsonl":0,"tmp\\/Inspec.test.jsonl":0,"tmp\\/Inspec.train.jsonl":0,"tmp\\/PubMed-titles.test.jsonl":0,"tmp\\/acm-dl.test.jsonl":0},"tmp\\/Inspec.test.jsonl":{"ACM-abstract.test.jsonl":0,"KDD.test.jsonl":0,"KP20k.test.jsonl":4,"KP20k\\/full\\/kp20k.train.json":59,"KP20k\\/full\\/kp20k.valid.json":2,"NTCIR1+2.test.jsonl":1,"SemEval-2010-abstract.test.jsonl":0,"WWW.test.jsonl":0,"tmp\\/Inspec.dev.jsonl":0,"tmp\\/Inspec.test.jsonl":0,"tmp\\/Inspec.train.jsonl":0,"tmp\\/PubMed-titles.test.jsonl":0,"tmp\\/acm-dl.test.jsonl":0},"tmp\\/Inspec.train.jsonl":{"ACM-abstract.test.jsonl":6,"KDD.test.jsonl":0,"KP20k.test.jsonl":7,"KP20k\\/full\\/kp20k.train.json":154,"KP20k\\/full\\/kp20k.valid.json":5,"NTCIR1+2.test.jsonl":0,"SemEval-2010-abstract.test.jsonl":0,"WWW.test.jsonl":0,"tmp\\/Inspec.dev.jsonl":0,"tmp\\/Inspec.test.jsonl":0,"tmp\\/Inspec.train.jsonl":0,"tmp\\/PubMed-titles.test.jsonl":0,"tmp\\/acm-dl.test.jsonl":0},"tmp\\/PubMed-titles.test.jsonl":{"ACM-abstract.test.jsonl":0,"KDD.test.jsonl":0,"KP20k.test.jsonl":2,"KP20k\\/full\\/kp20k.train.json":11,"KP20k\\/full\\/kp20k.valid.json":0,"NTCIR1+2.test.jsonl":0,"SemEval-2010-abstract.test.jsonl":0,"WWW.test.jsonl":0,"tmp\\/Inspec.dev.jsonl":0,"tmp\\/Inspec.test.jsonl":0,"tmp\\/Inspec.train.jsonl":0,"tmp\\/PubMed-titles.test.jsonl":0,"tmp\\/acm-dl.test.jsonl":1},"tmp\\/acm-dl.test.jsonl":{"ACM-abstract.test.jsonl":279,"KDD.test.jsonl":676,"KP20k.test.jsonl":734,"KP20k\\/full\\/kp20k.train.json":19539,"KP20k\\/full\\/kp20k.valid.json":729,"NTCIR1+2.test.jsonl":8,"SemEval-2010-abstract.test.jsonl":26,"WWW.test.jsonl":1237,"tmp\\/Inspec.dev.jsonl":0,"tmp\\/Inspec.test.jsonl":0,"tmp\\/Inspec.train.jsonl":0,"tmp\\/PubMed-titles.test.jsonl":1,"tmp\\/acm-dl.test.jsonl":1356}}')


clean_columns = lambda x: x.replace('.jsonl', '').replace('.json', '').replace('KP20k/full/', '').replace('tmp/', '')
df = pd.DataFrame(mat)
df = df.rename(columns=clean_columns).rename(index=clean_columns)

df_disp = df.applymap(lambda x: x if x else -100)
sns.heatmap(df_disp, annot=True, fmt='d', vmin=-100, vmax=100, mask=(df_disp == -100))
plt.show()

# Document en commun entre kp20k.train et les ensembles de tests
df['kp20k.train'][set(df.columns) - set(c for c in df.columns if 'test' in c)]
