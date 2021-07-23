# Compute results for YAKE and YAKE2

import os; from glob import glob; import pke; from tqdm import tqdm; import json; from itertools import product

corpus_path = {c: os.path.join(os.environ['PATH_AKE_DATASETS'], 'datasets', c, 'test') for c in ['110-PT-BN-KP', '500N-KPCrowd', 'Inspec', 'PubMed', 'SemEval-2010']}
res = {}
for c, c_p in corpus_path.items():
    file_path = glob(c_p + os.sep + '*')
    file_path = [f for f in file_path if not f.endswith('txt')]
    if not file_path:
        print(c)
        continue 
    o = False   
    for s, e, p in product([False], [False], [False]):
        k = c + ('.use_stem' if s else '') + ('.ecir' if e else '') + ('.nopool' if not p else '') + ('.use_max' if o else '')
        if k in res:
            continue
        output_file_path = os.path.join(os.environ['HOME'], 'ake-benchmarking', 'output_yake', k + '.YAKE.stem.json')
        if os.path.isfile(output_file_path) and input(f'Output file already exists : {output_file_path}. Overwrite ? (y/(n))').lower() != 'y':
            print('Not writing.')
            continue
        res[k] = {}
        for p in tqdm(file_path, desc=k):
            a = pke.unsupervised.YAKE2()
            a.load_document(p)
            a.candidate_selection()
            a.candidate_weighting(use_stems=s, ecir=e, pool_best=p)
            res[k][os.path.basename(p).rsplit('.', 1)[0]] = [[r] for r, _ in a.get_n_best(20, stemming=True)]
        assert len(file_path) == len(res[k])
        with open(output_file_path, 'w') as f:
            json.dump(res[k], f)


# create dataframe python evaluate_glob.py 'output_yake/*.stem.json' > output_yake/res.txt

# Display result dataframe
import pandas as pd
with open('output_yake/res.txt') as f:
    tmp = f.read()
    df = pd.DataFrame([[c.strip() for c in l.split('|') if c.strip()] for l in tmp.split('\n')
if l.strip()], columns=['P', 'R', 'F', 'MAP', 'N', 'file'])
    df['corpus'] = df['file'].apply(lambda x: x.split('.')[0])
    df['opt'] = df['file'].apply(lambda r: ('s' if 'use_stem' in r else '') + ('e' if 'ecir' i
n r else '') + ('p' if 'nopool' in r else '') + ('m' if 'use_max' in r else ''))
    df['meth'] = df['file'].apply(lambda x: x.split('.')[-3])
df.groupby(['corpus', 'meth', 'opt'])['MAP'].max().unstack(2)


import pke
file = '../../../../ake-datasets/datasets/110-PT-BN-KP/test/2000_10_09-13_00_00-JornaldaTarde-8-topic-seg.txt-Nr10.xml'
a1 = pke.unsupervised.YAKE(); a1.load_document(file); a1.candidate_selection(); a1.candidate_weighting(); e1 = a1.weights
a2 = pke.unsupervised.YAKE2(); a2.load_document(file); a2.candidate_selection(); a2.candidate_weighting(pool_best=False); e2 = {k: -v for k, v in a2.weights.items()}