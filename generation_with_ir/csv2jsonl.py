import re
import json
from tqdm import tqdm
import string

punct_tab = str.maketrans(dict.fromkeys(string.punctuation))
for c in '\t\n \r':  # add whitespace characters
    punct_tab[ord(c)] = None


def preproc(title):
    return title.strip().lower().translate(punct_tab)


def read_until(f):
    acc = []
    for l in f:
        l = l.decode('utf-8')
        if not re.match(r'\d+\t\d+(\.\d+)+\t\d+\t', l):
            # Not a new row :'( WTF
            print('Pbm: ', l)
            continue
        l = l.split('\t')
        if acc and l[0] != acc[-1][0]:
            yield acc
            acc = [l]
        else:
            acc.append(l)
    yield acc


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
    with open(path) as g:
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
                title_mapping[pr_title].append((id_, og_title, fp, k))
            else:
                title_mapping[pr_title] = [(id_, og_title, fp, k)]


# Choose mapping from acm-dl if exists else with the least kw
# (annnotation with the most keyword doesn't seem to match author keyphrases)
kws = {}
for k, v in title_mapping.items(): 
    matches = sorted(v['matches'], key=lambda x: ('acm-dl' in x['file'], x['keyword'].count(';')), reverse=True)
    # You can keep other info such as 
    kws[k] = matches[0]['keyword']


with open('data.csv', 'rb') as f:
    columns = next(f).decode('utf-8').strip().split('\t')
    columns[1] = 'id'
    columns[2] = 'citationcontext_id'
    not_processed = []
    f= tqdm(f, total=12296856)
    f = read_until(f)
    g = open('data.jsonl', 'w')
    for lines in f:
        lines = [[e.strip() for e in l] for l in lines]
        # All the values in 0, 1, 3, 4, 5 should be common to every line
        if any(not l[i] for i in [0, 1, 3, 4, 5] for l in lines):
            not_processed.append(lines)
            continue
        # Removing lines that do not have a citation context or a citation context id
        to_keep = [i for i in range(len(lines)) if lines[i][2] and lines[i][6]]
        to_remove = set(range(len(lines))) - set(to_keep)
        not_processed.append([lines[i] for i in to_remove])
        lines = [lines[i] for i in to_keep]

        cur_j = {columns[i]: lines[0][i].strip() for i in [0, 1, 3, 4, 5]}
        # Search the title in kws
        pr_title = preproc(cur_j['title'])
        if pr_title in kws:
            cur_j['keyword'] = kws[pr_title]
        cur_j['ctxt'] = [(l[2].strip(), l[-1].strip()) for l in lines if '=-=' in l[-1]]
        g.write(json.dumps(cur_j) + '\n')
    g.close()
