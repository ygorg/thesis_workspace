# Explore abs_pres models

from pprint import pprint as print
import json


copied_abs = 'experiments/copy_abs-b9d6765/predictions/KP20k.7.test.jsonl.jsonl'
with open(copied_abs) as f:
    data = [json.loads(line) for line in f]
copied_abs = [list(filter(None, [[(i, j, d['predicted_tokens'][i][j]) for j, t in enumerate(k) if t > 50002]for i, k in enumerate(d['predictions'])])) for d in data]

copied_prs = 'experiments/copy_pres-b9d6765/predictions/KP20k.5.test.jsonl.jsonl'
with open(copied_prs) as f:
    data = [json.loads(line) for line in f]
copied_prs = [list(filter(None, [[(i, j, d['predicted_tokens'][i][j]) for j, t in enumerate(k) if t > 50002] for i, k in enumerate(d['predictions'])])) for d in data]

copied_les = 'experiments/copy_less-012a145/predictions/KP20k.jsonl'
with open(copied_les) as f:
    data = [json.loads(line) for line in f]

copied_les = [list(filter(None, [[(i, j, d['predicted_tokens'][i][j]) for j, t in enumerate(k) if t > 50002] for i, k in enumerate(d['predictions'])])) for d in data]

sum(map(len, copied_abs))/len(copied_abs)
sum(map(len, copied_prs))/len(copied_prs)
sum(map(len, copied_les))/len(copied_les)


sum(len(k for k in d if k[0][0] < 10)/10 for d in copied_abs)/len(copied_abs)
sum(len(k for k in d if k[0][0] < 10)/10 for d in copied_prs)/len(copied_prs)
sum(len(k for k in d if k[0][0] < 10)/10 for d in copied_les)/len(copied_les)

c_abs = Counter([t[2] for d in copied_abs for k in d if k[0][0] < 10 for t in k])
c_prs = Counter([t[2] for d in copied_prs for k in d if k[0][0] < 10 for t in k])
c_les = Counter([t[2] for d in copied_les for k in d if k[0][0] < 10 for t in k])





abs = 'experiments/copy_abs-b9d6765/predictions/KP20k.7.test.jsonl.stem.json'
prs = 'experiments/copy_pres-b9d6765/predictions/KP20k.5.test.jsonl.stem.json'
all_ = 'experiments/copy_less-012a145/predictions/KP20k.test.stem.json'
with open(abs) as f:
    abs = json.load(f)

with open(prs) as f:
    prs = json.load(f)

with open(all_) as f:
    all_ = json.load(f)

for k in abs:
    ab = [v for k in abs[k][:10] for v in k]
    pr = [v for k in prs[k][:10] for v in k]
    al = [v for k in all_[k][:10] for v in k]
    if ab != pr and pr != al:
        print((k, len(set(ab) & set(pr) & set(al))))
        print(['{:15} & {:15} & {:15}'.format(a, b, c) for a, b, c in zip(ab, pr, al)])
        if input() == ' ':
            break 