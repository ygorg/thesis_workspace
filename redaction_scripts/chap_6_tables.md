## Tableau ir_per_domain

```python
data = []
for meth in ['', '-MultipartiteRank', '-KeaOneModel', '-CorrRNN', '-CopyRNN']:
    acc = []
    for kps in ['', '-all']:
        for domain in [1, 2]:
            model = 'bm25'
            # The baseline is the same system but without predicted keywords
            baseline = load_scores(f'data/ntcir-2/output/run.ntcir-2-t+a{kps}.description.{model}.results')
            baseline = [v for k, v in baseline.items() if domains.get(k, []) == [domain]]
            baseline_score = sum(baseline) / len(baseline)

            system_ = load_scores(f'data/ntcir-2/output/run.ntcir-2-t+a{kps}{meth}.description.{model}.results')
            system_ = [v for k, v in system_.items() if domains.get(k, []) == [domain]]
            system_score = sum(system_) / len(system_)

            ttest = stats.ttest_rel(a=baseline, b=system_)[1]
            sign = ttest < .05

            diff_score = system_score - baseline_score

            tmp_d = 'I' if domain == 1 else 'O'
            tmp_k = 'tak' if kps[1:] else 'ta'
            data.append((meth[1:], tmp_k, tmp_d, system_score, diff_score, sign))

df = pd.DataFrame(data, columns=['m', 'k', 'd', 's', 'diff', 'sign'])
df['is_max'] = df.groupby(['k', 'd'])['s'].transform('max') == df['s']
df['print_s'] = df.apply(lambda x: stylee(round(x['s']*100, 1), x['sign'], x['is_max'], x['diff']) + (' ' +
                                   add_latex_command('ddiff', round(x['diff']*100, 1)) if round(x['diff'], 3) else ''), axis=1)

```


### Créer référence par domaine

```python
import json
from collections import defaultdict

ROOT = '/home/gallina/'

with open(f'{ROOT}/ir-using-kg/data/topics/domains.json') as f:
    domains = json.load(f)

qrel = load_qrel(f'{ROOT}/redefining-absent-keyphrases/data/ntcir-2/qrels/rel1_ntc2-e2_0101-0149.qrels')

path_ake_datasets = f'{ROOT}/ake-datasets/datasets/'

with open(f'{path_ake_datasets}/NTCIR1+2/references/test.indexer.stem.json') as f:
    ref = json.load(f)

in_domain_ref = {}
out_domain_ref = {}
for k in domains:
    if domains[k] == [1]:
        for doc_id in qrel[k]:
            if doc_id in ref:
                in_domain_ref[doc_id] = ref[doc_id]
    elif domains[k] == [2]:
        for doc_id in qrel[k]:
            if doc_id in ref:
                out_domain_ref[doc_id] = ref[doc_id]

with open(f'{path_ake_datasets}/NTCIR1+2/references/test.indexer_in.stem.json', 'w') as f:
    json.dump(in_domain_ref, f)
with open(f'{path_ake_datasets}/NTCIR1+2/references/test.indexer_out.stem.json', 'w') as f:
    json.dump(out_domain_ref, f)
```

```bash
cd "/home/gallina/ake-benchmarking"
for DOM in "in" "out"
do
    echo ${DOM}
    for METH in "MultipartiteRank" "KeaOneModel" "CorrRNN" "CopyRNN"
    do
        python3 eval.py -i "output/NTCIR1+2/NTCIR1+2.${METH}.stem.json" \
                        -r "../ake-datasets/datasets/NTCIR1+2/references/test.indexer_${DOM}.stem.json" \
                        -n 5
    done
done

rm "/home/gallina/ake-datasets/datasets/NTCIR1+2/references/test.indexer_*.stem.json"
```


## Load scores

```python
import os
import gzip
import pandas as pd
from tqdm import tqdm
from glob import glob
from io import StringIO
from scipy import stats
from collections import defaultdict


def load_scores(p):
    data = {}
    with open(p) as f:
        for line in f:
            metric, qid, sc = line.strip().split('\t')
            if metric.strip() == 'recall_1000':
                continue
            data[qid] = float(sc)
    return data


def mean(values):
    return sum(values) / len(values)


def param_to_file(coll, sys_, r, m, n, p, out):
    if m and not n or p and not m:
        raise ArgumentError()
    if n is not None:
        n = str(n)
    tmp = list(filter(None, [r, m, n, p]))
    if tmp:
        tmp = '-' + '-'.join(tmp)
    else:
        tmp = ''

    exp_ = f'{coll}-t+a{tmp}'
    home_ = '/home/gallina/redefining-absent-keyphrases'
    output_ = f'{home_}/data/{coll}/output/run.{exp_}.description.{sys_}'

    out_dict = {'req': output_+'.req',
     None: output_,
     'res': output_ + '.results',
     'txt': output_ + '.txt',
     'col': glob(f'{home_}/data/{coll}/collections/{exp_}/*.gz')[0]
    }
    return out_dict[out]


def exp_to_param(exp):
    """{coll}-t+a{tmp}"""
    exp_ = exp.split('-')[3:]
    if not exp_:
        exp_ = ['none'] * 4
    elif exp_[0][0].islower():
        # there are reference keyphrases
        exp_ += ['none'] * (4 - len(exp_))
    else:
        # there are reference keyphrases
        exp_ = ['none'] + exp_ + ['none'] * (3 - len(exp_))
    return exp_


def file_to_param(f):
    """/home/gallina/redefining-absent-keyphrases/data/{coll}/output/run.{coll}-t+a{tmp}.description.{sys_}.results"""
    coll = f.split(os.sep)[-3]
    exp, _, sys_ = os.path.basename(f).split('.')[1:4]
    r, m, n, p = exp_to_param(exp)
    return coll, sys_, r, m, n, p



def compute_kw_number():
    exp_to_param('a-a-a-a-a')
    def extract_content(tagged_line, tag):
        """Extract content from SGML line."""
        return tagged_line.replace("<"+tag+">", "").replace("</"+tag+">","")

    import os
    import gzip
    import pandas as pd
    from tqdm import tqdm
    from glob import glob
    from collections import defaultdict
    data = {}
    for file_path in tqdm(
            glob('/home/gallina/redefining-absent-keyphrases/data/ntcir-2/collections/*/*.gz') +
            glob('/home/gallina/redefining-absent-keyphrases/data/acm-cr/collections/*/*.gz')):
        all_keyphrases = defaultdict(lambda: 0)

        with gzip.open(file_path, 'rt') as f:
            doc_id = None
            title = None
            text = None
            keyphrases = None
            is_in_document = False

            for i, line in enumerate(f):
                line = line.strip()
                if line.startswith('<DOC>'):
                    is_in_document = True
                elif line.startswith('<DOCNO>'):
                    doc_id = extract_content(line, "DOCNO")
                elif line.startswith('<TITLE>') or line.startswith('<TEXT>'):
                    ()
                elif line.startswith('<HEAD>'):
                    keyphrases = extract_content(line, "HEAD")
                    keyphrases = [k.strip() for k in keyphrases.split("//")]
                    all_keyphrases[doc_id] += len(keyphrases)
                elif line.startswith('</DOC>'):
                    if doc_id not in all_keyphrases:
                        all_keyphrases[doc_id] = 0
                    doc_id = None
                    title = None
                    text = None
                    keyphrases = None
                    is_in_document = False
                elif is_in_document:
                    print("parse error at line {}".format(str(i)))
                    exit(0)
        if all_keyphrases:
            data[file_path] = sum(all_keyphrases.values()) / len(all_keyphrases)
        else:
            data[file_path] = 0

    return pd.DataFrame([[k.split(os.sep)[-4]] + exp_to_param(k.split(os.sep)[-2]) + [round(v, 1)] for k, v in data.items()], columns=['coll', 'ref', 'method', 'n', 'prmu', 'nb_kws'])


def add_latex_command(command, value):
    return f'\\{command}{{{value}}}'


def stylee(row, agg=None):
    assert len(row) == 1
    row = row[0]
    v = round(row['value'], 1)
    s, b = row['sign'], row.get('is_best', False)

    if row['variable'] == 'score':
        val2com = {(True, True): 'bests', (True, False): 'best', (False, True): 'sign'}
        if (b, s) in val2com:
            return add_latex_command(val2com[(b, s)], v)
        else:
            return f'{v}'

    elif row['variable'] == 'diff':
        if v:
            return add_latex_command('ddiff', v)
        else:
            return ' '
    else:
        return f'{v}'


files = glob('/home/gallina/redefining-absent-keyphrases/data/ntcir-2/output/*.results')
files += glob('/home/gallina/redefining-absent-keyphrases/data/acm-cr/output/*.results')


data = []
for f in files:
    coll, sys_, r, m, n, p = file_to_param(f)
    s = load_scores(f)
    s.pop('all')
    mean_s = mean(s.values()) * 100

    s_baseline = load_scores(param_to_file(coll, sys_, None if r == 'none' else r, None, None, None, 'res'))
    s_baseline.pop('all')
    mean_s_baseline = mean(s_baseline.values()) * 100

    tmp_keys = list(s_baseline)
    ttest = stats.ttest_rel(a=[s[k] for k in tmp_keys], b=[s_baseline[k] for k in tmp_keys])[1]
    sign = ttest < .05


    s_no_kw = load_scores(param_to_file(coll, sys_, None, None, None, None, 'res'))
    s_no_kw.pop('all')
    mean_s_no_kw = mean(s_no_kw.values()) * 100

    tmp_keys = list(s_baseline)
    ttest = stats.ttest_rel(a=[s[k] for k in tmp_keys], b=[s_baseline[k] for k in tmp_keys])[1]
    sign_no_kw = ttest < .05

    data.append([coll, r, m, n, p, sys_, mean_s, sign, mean_s - mean_s_baseline, sign_no_kw, mean_s - mean_s_no_kw, f])

df = pd.DataFrame(data, columns=['collection', 'ref', 'method', 'n', 'prmu', 'system', 'score', 'sign', 'diff', 'sign_nokw', 'diff_no_kw', 'file_path'])
# df_nb_kws = compute_kw_number()
df_nb_kws = pd.read_csv(StringIO('coll,ref,method,n,prmu,nb_kws\nntcir-2,none,none,none,none,0.0\nntcir-2,all,none,none,none,4.7\nntcir-2,p,none,none,none,2.9\nntcir-2,r,none,none,none,0.4\nntcir-2,m,none,none,none,0.8\nntcir-2,u,none,none,none,0.7\nntcir-2,rmu,none,none,none,1.8\nntcir-2,pr,none,none,none,3.3\nntcir-2,mu,none,none,none,1.5\nntcir-2,all,CopyRNN,5,m,6.0\nntcir-2,none,CopyRNN,5,pr,5.0\nntcir-2,none,CopyRNN,5,rmu,4.1\nntcir-2,none,CorrRNN,5,r,1.9\nntcir-2,none,CorrRNN,5,u,0.1\nntcir-2,none,CorrRNN,5,mu,0.4\nntcir-2,all,CorrRNN,1,none,5.7\nntcir-2,all,CorrRNN,2,none,6.7\nntcir-2,none,CorrRNN,3,none,3.0\nntcir-2,none,CorrRNN,4,none,4.0\nntcir-2,none,CorrRNN,6,none,6.0\nntcir-2,all,CorrRNN,6,none,10.7\nntcir-2,all,CorrRNN,7,none,11.7\nntcir-2,all,CorrRNN,8,none,12.7\nntcir-2,none,CorrRNN,9,none,8.9\nntcir-2,none,CopyRNN,5,p,5.0\nntcir-2,all,CopyRNN,5,p,9.7\nntcir-2,all,CopyRNN,5,r,8.3\nntcir-2,none,CopyRNN,5,u,1.2\nntcir-2,all,CopyRNN,5,pr,9.7\nntcir-2,all,CopyRNN,5,rmu,8.9\nntcir-2,all,CorrRNN,5,r,6.6\nntcir-2,all,CorrRNN,5,u,4.8\nntcir-2,all,CorrRNN,5,mu,5.1\nntcir-2,all,KeaOneModel,1,none,5.7\nntcir-2,none,CopyRNN,5,none,5.0\nntcir-2,all,CopyRNN,5,none,9.7\nntcir-2,none,CorrRNN,5,none,5.0\nntcir-2,all,CorrRNN,5,none,9.7\nntcir-2,none,KeaOneModel,5,none,5.0\nntcir-2,all,KeaOneModel,5,none,9.7\nntcir-2,none,MultipartiteRank,5,none,5.0\nntcir-2,all,MultipartiteRank,5,none,9.7\nntcir-2,none,TfIdf,5,none,5.0\nntcir-2,all,TfIdf,5,none,9.7\nntcir-2,none,TfIdfOneModel,5,none,5.0\nntcir-2,all,TfIdfOneModel,5,none,9.7\nntcir-2,none,CopyRNN,1,none,1.0\nntcir-2,all,CopyRNN,1,none,5.7\nntcir-2,none,CopyRNN,2,none,2.0\nntcir-2,all,CopyRNN,2,none,6.7\nntcir-2,none,CopyRNN,3,none,3.0\nntcir-2,all,CopyRNN,3,none,7.7\nntcir-2,none,CopyRNN,4,none,4.0\nntcir-2,all,CopyRNN,4,none,8.7\nntcir-2,none,CopyRNN,6,none,6.0\nntcir-2,all,CopyRNN,6,none,10.7\nntcir-2,none,CopyRNN,7,none,7.0\nntcir-2,all,CopyRNN,7,none,11.7\nntcir-2,none,CopyRNN,8,none,8.0\nntcir-2,all,CopyRNN,8,none,12.7\nntcir-2,none,CopyRNN,9,none,9.0\nntcir-2,all,CopyRNN,9,none,13.7\nntcir-2,none,CopyRNN,5,r,3.5\nntcir-2,none,CopyRNN,5,m,1.2\nntcir-2,all,CopyRNN,5,u,6.0\nntcir-2,none,CopyRNN,5,mu,2.0\nntcir-2,none,CorrRNN,5,p,5.0\nntcir-2,none,CorrRNN,5,m,0.3\nntcir-2,none,CorrRNN,5,pr,5.0\nntcir-2,none,CorrRNN,5,rmu,2.2\nntcir-2,none,CorrRNN,1,none,1.0\nntcir-2,none,CorrRNN,2,none,2.0\nntcir-2,all,CorrRNN,3,none,7.7\nntcir-2,all,CorrRNN,4,none,8.7\nntcir-2,none,CorrRNN,7,none,7.0\nntcir-2,none,CorrRNN,8,none,8.0\nntcir-2,all,CorrRNN,9,none,13.7\nntcir-2,all,CopyRNN,5,mu,6.8\nntcir-2,all,CorrRNN,5,p,9.7\nntcir-2,all,CorrRNN,5,m,5.1\nntcir-2,all,CorrRNN,5,pr,9.7\nntcir-2,none,KeaOneModel,1,none,1.0\nntcir-2,none,KeaOneModel,2,none,2.0\nntcir-2,all,KeaOneModel,2,none,6.7\nntcir-2,none,KeaOneModel,3,none,3.0\nntcir-2,all,KeaOneModel,3,none,7.7\nntcir-2,none,KeaOneModel,4,none,4.0\nntcir-2,all,KeaOneModel,4,none,8.7\nntcir-2,none,KeaOneModel,6,none,6.0\nntcir-2,all,KeaOneModel,6,none,10.7\nntcir-2,none,KeaOneModel,7,none,7.0\nntcir-2,all,KeaOneModel,7,none,11.7\nntcir-2,none,KeaOneModel,8,none,8.0\nntcir-2,all,KeaOneModel,8,none,12.7\nntcir-2,none,KeaOneModel,9,none,9.0\nntcir-2,all,KeaOneModel,9,none,13.7\nntcir-2,none,MultipartiteRank,1,none,1.0\nntcir-2,all,MultipartiteRank,1,none,5.7\nntcir-2,none,MultipartiteRank,2,none,2.0\nntcir-2,all,MultipartiteRank,2,none,6.7\nntcir-2,none,MultipartiteRank,3,none,3.0\nntcir-2,all,MultipartiteRank,3,none,7.7\nntcir-2,none,MultipartiteRank,4,none,4.0\nntcir-2,all,MultipartiteRank,4,none,8.7\nntcir-2,none,MultipartiteRank,6,none,6.0\nntcir-2,all,MultipartiteRank,6,none,10.7\nntcir-2,none,MultipartiteRank,7,none,7.0\nntcir-2,all,MultipartiteRank,7,none,11.7\nntcir-2,none,MultipartiteRank,8,none,8.0\nntcir-2,all,MultipartiteRank,8,none,12.7\nntcir-2,none,MultipartiteRank,9,none,9.0\nntcir-2,all,MultipartiteRank,9,none,13.7\nntcir-2,none,TfIdf,1,none,1.0\nntcir-2,all,TfIdf,1,none,5.7\nntcir-2,none,TfIdf,2,none,2.0\nntcir-2,all,TfIdf,2,none,6.7\nntcir-2,none,TfIdf,3,none,3.0\nntcir-2,all,TfIdf,3,none,7.7\nntcir-2,none,TfIdf,4,none,4.0\nntcir-2,all,TfIdf,4,none,8.7\nntcir-2,none,TfIdf,6,none,6.0\nntcir-2,all,TfIdf,6,none,10.7\nntcir-2,none,TfIdf,7,none,7.0\nntcir-2,all,TfIdf,7,none,11.7\nntcir-2,none,TfIdf,8,none,8.0\nntcir-2,all,TfIdf,8,none,12.7\nntcir-2,none,TfIdf,9,none,9.0\nntcir-2,all,TfIdf,9,none,13.7\nntcir-2,none,TfIdfOneModel,1,none,1.0\nntcir-2,all,TfIdfOneModel,1,none,5.7\nntcir-2,none,TfIdfOneModel,2,none,2.0\nntcir-2,all,TfIdfOneModel,2,none,6.7\nntcir-2,none,TfIdfOneModel,3,none,3.0\nntcir-2,all,TfIdfOneModel,3,none,7.7\nntcir-2,none,TfIdfOneModel,4,none,4.0\nntcir-2,all,TfIdfOneModel,4,none,8.7\nntcir-2,none,TfIdfOneModel,6,none,6.0\nntcir-2,all,TfIdfOneModel,6,none,10.7\nntcir-2,none,TfIdfOneModel,7,none,7.0\nntcir-2,all,TfIdfOneModel,7,none,11.7\nntcir-2,none,TfIdfOneModel,8,none,8.0\nntcir-2,all,TfIdfOneModel,8,none,12.7\nntcir-2,none,TfIdfOneModel,9,none,9.0\nntcir-2,all,TfIdfOneModel,9,none,13.7\nntcir-2,all,CorrRNN,5,rmu,6.9\nacm-cr,none,none,none,none,0.0\nacm-cr,all,none,none,none,3.1\nacm-cr,p,none,none,none,1.6\nacm-cr,r,none,none,none,0.3\nacm-cr,m,none,none,none,0.6\nacm-cr,u,none,none,none,0.5\nacm-cr,rmu,none,none,none,1.5\nacm-cr,pr,none,none,none,2.0\nacm-cr,mu,none,none,none,1.1\nacm-cr,none,MultipartiteRank,1,none,1.0\nacm-cr,none,MultipartiteRank,2,none,2.0\nacm-cr,none,MultipartiteRank,3,none,2.9\nacm-cr,none,MultipartiteRank,4,none,3.8\nacm-cr,all,MultipartiteRank,4,none,7.0\nacm-cr,all,MultipartiteRank,6,none,8.7\nacm-cr,all,MultipartiteRank,7,none,9.6\nacm-cr,none,MultipartiteRank,8,none,7.3\nacm-cr,none,MultipartiteRank,9,none,8.2\nacm-cr,none,CopyRNN,5,none,5.0\nacm-cr,all,CopyRNN,5,none,8.1\nacm-cr,none,CorrRNN,5,none,5.0\nacm-cr,all,CorrRNN,5,none,8.1\nacm-cr,none,KeaOneModel,5,none,4.7\nacm-cr,all,KeaOneModel,5,none,7.9\nacm-cr,none,MultipartiteRank,5,none,4.7\nacm-cr,all,MultipartiteRank,5,none,7.9\nacm-cr,none,TfIdf,5,none,4.7\nacm-cr,all,TfIdf,5,none,7.9\nacm-cr,none,TfIdfOneModel,5,none,4.7\nacm-cr,all,TfIdfOneModel,5,none,7.9\nacm-cr,none,CopyRNN,1,none,1.0\nacm-cr,all,CopyRNN,1,none,4.1\nacm-cr,none,CopyRNN,2,none,2.0\nacm-cr,all,CopyRNN,2,none,5.1\nacm-cr,none,CopyRNN,3,none,3.0\nacm-cr,all,CopyRNN,3,none,6.1\nacm-cr,none,CopyRNN,4,none,4.0\nacm-cr,all,CopyRNN,4,none,7.1\nacm-cr,none,CopyRNN,6,none,6.0\nacm-cr,all,CopyRNN,6,none,9.1\nacm-cr,none,CopyRNN,7,none,7.0\nacm-cr,all,CopyRNN,7,none,10.1\nacm-cr,none,CopyRNN,8,none,8.0\nacm-cr,all,CopyRNN,8,none,11.1\nacm-cr,none,CopyRNN,9,none,9.0\nacm-cr,all,CopyRNN,9,none,12.1\nacm-cr,none,CorrRNN,1,none,1.0\nacm-cr,all,CorrRNN,1,none,4.1\nacm-cr,none,CorrRNN,2,none,2.0\nacm-cr,all,CorrRNN,2,none,5.1\nacm-cr,none,CorrRNN,3,none,3.0\nacm-cr,all,CorrRNN,3,none,6.1\nacm-cr,none,CorrRNN,4,none,4.0\nacm-cr,all,CorrRNN,4,none,7.1\nacm-cr,none,CorrRNN,6,none,6.0\nacm-cr,all,CorrRNN,6,none,9.1\nacm-cr,none,CorrRNN,7,none,6.9\nacm-cr,all,CorrRNN,7,none,10.1\nacm-cr,none,CorrRNN,8,none,7.8\nacm-cr,all,CorrRNN,8,none,11.0\nacm-cr,none,CorrRNN,9,none,8.7\nacm-cr,all,CorrRNN,9,none,11.8\nacm-cr,none,KeaOneModel,1,none,1.0\nacm-cr,all,KeaOneModel,1,none,4.1\nacm-cr,none,KeaOneModel,2,none,2.0\nacm-cr,all,KeaOneModel,2,none,5.1\nacm-cr,none,KeaOneModel,3,none,2.9\nacm-cr,all,KeaOneModel,3,none,6.1\nacm-cr,none,KeaOneModel,4,none,3.8\nacm-cr,all,KeaOneModel,4,none,7.0\nacm-cr,none,KeaOneModel,6,none,5.6\nacm-cr,all,KeaOneModel,6,none,8.7\nacm-cr,none,KeaOneModel,7,none,6.5\nacm-cr,all,KeaOneModel,7,none,9.6\nacm-cr,none,KeaOneModel,8,none,7.3\nacm-cr,all,KeaOneModel,8,none,10.5\nacm-cr,none,KeaOneModel,9,none,8.2\nacm-cr,all,KeaOneModel,9,none,11.4\nacm-cr,all,MultipartiteRank,1,none,4.1\nacm-cr,all,MultipartiteRank,2,none,5.1\nacm-cr,all,MultipartiteRank,3,none,6.1\nacm-cr,none,MultipartiteRank,6,none,5.6\nacm-cr,none,MultipartiteRank,7,none,6.5\nacm-cr,all,MultipartiteRank,8,none,10.5\nacm-cr,all,MultipartiteRank,9,none,11.4\nacm-cr,none,TfIdf,1,none,1.0\nacm-cr,all,TfIdf,1,none,4.1\nacm-cr,none,TfIdf,2,none,2.0\nacm-cr,all,TfIdf,2,none,5.1\nacm-cr,none,TfIdf,3,none,2.9\nacm-cr,all,TfIdf,3,none,6.1\nacm-cr,none,TfIdf,4,none,3.8\nacm-cr,all,TfIdf,4,none,7.0\nacm-cr,none,TfIdf,6,none,5.6\nacm-cr,all,TfIdf,6,none,8.7\nacm-cr,none,TfIdf,7,none,6.5\nacm-cr,all,TfIdf,7,none,9.6\nacm-cr,none,TfIdf,8,none,7.3\nacm-cr,all,TfIdf,8,none,10.5\nacm-cr,none,TfIdf,9,none,8.2\nacm-cr,all,TfIdf,9,none,11.4\nacm-cr,none,TfIdfOneModel,1,none,1.0\nacm-cr,all,TfIdfOneModel,1,none,4.1\nacm-cr,none,TfIdfOneModel,2,none,2.0\nacm-cr,all,TfIdfOneModel,2,none,5.1\nacm-cr,none,TfIdfOneModel,3,none,2.9\nacm-cr,all,TfIdfOneModel,3,none,6.1\nacm-cr,none,TfIdfOneModel,4,none,3.8\nacm-cr,all,TfIdfOneModel,4,none,7.0\nacm-cr,none,TfIdfOneModel,6,none,5.6\nacm-cr,all,TfIdfOneModel,6,none,8.7\nacm-cr,none,TfIdfOneModel,7,none,6.5\nacm-cr,all,TfIdfOneModel,7,none,9.6\nacm-cr,none,TfIdfOneModel,8,none,7.3\nacm-cr,all,TfIdfOneModel,8,none,10.5\nacm-cr,none,TfIdfOneModel,9,none,8.2\nacm-cr,all,TfIdfOneModel,9,none,11.4\nacm-cr,none,CopyRNN,5,p,5.0\nacm-cr,all,CopyRNN,5,p,8.1\nacm-cr,none,CopyRNN,5,r,2.4\nacm-cr,all,CopyRNN,5,r,5.5\nacm-cr,none,CopyRNN,5,m,1.8\nacm-cr,all,CopyRNN,5,m,4.9\nacm-cr,none,CopyRNN,5,u,2.8\nacm-cr,all,CopyRNN,5,u,5.9\nacm-cr,none,CopyRNN,5,pr,5.0\nacm-cr,all,CopyRNN,5,pr,8.1\nacm-cr,none,CopyRNN,5,mu,3.6\nacm-cr,all,CopyRNN,5,mu,6.7\nacm-cr,none,CopyRNN,5,rmu,4.5\nacm-cr,all,CopyRNN,5,rmu,7.7\nacm-cr,none,CorrRNN,5,p,5.0\nacm-cr,all,CorrRNN,5,p,8.1\nacm-cr,none,CorrRNN,5,r,1.2\nacm-cr,all,CorrRNN,5,r,4.3\nacm-cr,none,CorrRNN,5,m,0.3\nacm-cr,all,CorrRNN,5,m,3.4\nacm-cr,none,CorrRNN,5,u,0.4\nacm-cr,all,CorrRNN,5,u,3.5\nacm-cr,none,CorrRNN,5,pr,5.0\nacm-cr,all,CorrRNN,5,pr,8.1\nacm-cr,none,CorrRNN,5,mu,0.6\nacm-cr,all,CorrRNN,5,mu,3.8\nacm-cr,none,CorrRNN,5,rmu,1.8\nacm-cr,all,CorrRNN,5,rmu,4.9\n'))
df = pd.merge(df, df_nb_kws)
df_og = df
to_melt = ['score', 'sign', 'diff', 'sign_nokw', 'diff_no_kw']
to_keep = set(df.columns) - set(to_melt)
df = df.melt(to_keep)
```


## Tableau ir_all-abs-pres

```python
prepare_df = lambda df: df.groupby(['method', 'variable', 'prmu', 'ref', 'collection']).apply(lambda x: x.to_dict('records')).apply(stylee).unstack().unstack().unstack().unstack()

filtered_df = df[df['variable'] == 'score'][df['system'] == 'bm25+rm3'][df['ref'].isin(['none', 'all'])][df['method'].isin(['CopyRNN', 'CorrRNN'])][df['prmu'].isin(['rmu', 'p'])][df['n'] == '5']
pred = prepare_df(filtered_df)

filtered_df = df[df['variable'] == 'score'][df['system'] == 'bm25+rm3'][df['ref'].isin(['none', 'all'])][df['method'] == 'none'][df['prmu'] == 'none']
baseline = prepare_df(filtered_df).rename(index={'none': '-'}).rename(columns={'none': 'p'}, level=2)

out = pd.concat([baseline, pred]).reindex(['score', 'diff'], axis=1, level=3).reindex(['none', 'all'], axis=1, level=1).rename(columns={'none': '\\tr', 'all': '\\trm'})
print(out.to_latex(escape=False, multicolumn_format='c'))
```


## Tableau prmu_pred

```python
prmu_full_lst = ['none', 'pr', 'mu']
method_full_lst = ['CorrRNN', 'CopyRNN']
prmu2latex = {'p': '\\present', 'r': '\\reordonne', 'm': '\\mixte', 'u': '\\nonvu', 'none': 'P+R+M+U', 'rmu': 'Absent (RMU)', 'pr': 'Highlight (P+R)', 'mu': 'Expand (M+U)'}

# Predicted KW version
prepare_df = lambda df: df.melt(to_keep).groupby(['method', 'prmu', 'variable', 'system', 'ref', 'collection']).apply(lambda x: x.to_dict('records')).apply(stylee).unstack().unstack().unstack().unstack()

baseline = prepare_df(df[df['system'].isin(['bm25', 'bm25+rm3'])][df['method'] == 'none'][df['ref'].isin(['none', 'all'])]).rename(index={'none': '-'}, level=0)


pred_ = prepare_df(df[df['system'].isin(['bm25', 'bm25+rm3'])][df['n']=='5']).reindex(prmu_full_lst, level=1).rename(index=prmu2latex, level=1).reindex(method_full_lst, level=0)

out = pd.concat([baseline, pred_]).reindex(['score', 'nb_kws'], axis=1, level=3).reindex(['none', 'all'], axis=1, level=1).rename(columns={'none': '\\tr', 'all': '\\trm'}, level=1).reindex(['bm25+rm3'], axis=1, level=2)

print(out.to_latex(escape=False, multicolumn_format='c'))
```

## Tableau prmu_ref

```python
# Reference KW version
prmu_full_lst = ['p', 'r', 'm', 'u', 'rmu', 'pr', 'mu', 'none']
prmu2latex = {'p': '\\present', 'r': '\\reordonne', 'm': '\\mixte', 'u': '\\nonvu', 'none': 'P+R+M+U', 'rmu': 'Absent (RMU)', 'pr': 'Highlight (P+R)', 'mu': 'Expand (M+U)'}

prepare_df = lambda df: df.melt(to_keep).groupby(['ref', 'variable', 'system', 'collection']).apply(lambda x: x.to_dict('records')).apply(stylee).unstack().unstack().unstack()

ref = prepare_df(df).reindex(prmu_full_lst).rename(index=prmu2latex)

print(ref.to_latex(escape=False, multicolumn_format='c'))
```


## Tableau ir_results

```python
method_full_lst = ['none', 'MultipartiteRank', 'KeaOneModel', 'CorrRNN', 'CopyRNN']
method2latex = {'none': '-', 'MultipartiteRank': 'MPRank', 'KeaOneModel': 'Kea (KP20k)'}

system_full_lst = ['bm25', 'bm25+rm3', 'qld', 'qld+rm3']
system2latex = {'bm25': '\\textsc{Bm25}', 'bm25+rm3': 'B+RM3', 'qld': 'QL', 'qld+rm3': 'Q+RM3'}

prepare_df = lambda df: df.groupby(['ref', 'method', 'variable', 'system', 'collection']).apply(lambda x: x.to_dict('records')).apply(stylee).unstack().unstack().unstack()
table = prepare_df(df[df['ref'].isin(['none', 'all'])][df['n'] == '5'][df['prmu']=='none'])
baseline = prepare_df(df[df['ref'].isin(['none', 'all'])][df['method'] == 'none'])
table = pd.concat([baseline, table])

prepare_df2 = lambda df: df.groupby(['ref', 'method', 'variable', 'system', 'collection'])['value'].min()
table2 = prepare_df2(df[df['ref'].isin(['none', 'all'])][df['n'] == '5'][df['prmu']=='none'])
baseline2 = prepare_df2(df[df['ref'].isin(['none', 'all'])][df['method'] == 'none'])
mean_table = pd.concat([baseline2, table2])
mean_table = mean_table.groupby(['ref', 'method', 'variable', 'collection']).mean().unstack().round(1).apply(lambda x: x.apply(lambda pp: add_latex_command('diff', pp)) if x.name[2] == 'diff' else x, axis=1).unstack()
mean_table.columns = pd.MultiIndex.from_product([mean_table.columns.levels[0]] + [['mean']] + [mean_table.columns.levels[1]])

out = pd.concat([table, mean_table], axis=1).reindex(method_full_lst, level=1).rename(index=method2latex, level=1).rename(columns=system2latex, level=1).reindex(['score', 'diff'], axis=1, level=2).reindex(['none', 'all'], level=0).rename(index={'none': '\\tr', 'all': '\\trm'}, level=0)
print(out.to_latex(escape=False, multicolumn_format='c'))
```


## Figure n_vs_perf

```python

def roundPartial(value, resolution):
    return round(value / resolution) * resolution

print("""    \\begin{tikzpicture}[trim axis left,trim axis right]
    \\begin{groupplot}[
        group style={
          group size=1 by 2,
          vertical sep=1.3cm,
        },
        width=0.7\\textwidth, height=5cm,
        xmin=-1, xmax=10,
        xtick = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9},
        tick pos=left,
        grid style={dashed, gray!50},
        xmajorgrids,
        legend columns=-1,
        legend style={
            anchor=north west,
            at={(-0.09,-0.1)}
        }]""")
for ref in ['all', 'none']:

    filtered_df = df[df['system'] == 'bm25'][df['ref'] == ref][df['method'].isin(['CopyRNN', 'CorrRNN', 'MultipartiteRank', 'KeaOneModel'])][df['prmu'] == 'none'][df['variable'] == 'score']

    baseline = df[df['system'] == 'bm25'][df['ref'] == ref][df['method'] == 'none'][df['variable'] == 'score']
    assert len(baseline) == 1

    baseline = baseline['value'].values[0]

    max_ = max(filtered_df['value'].max(), baseline)
    max_ = roundPartial(max_, 0.25) + 0.25
    min_ = min(filtered_df['value'].min(), baseline)
    min_ = roundPartial(min_, 0.25) - 0.25

    if ref == 'all':
        print(f"""    \\nextgroupplot[
        ymin={min_}, ymax={max_},
        xticklabels={{,,,}},
        ytick = {{35, 36, 37}}]
    \\node[] at (axis cs: .4, {max_-0.5}) {{{{\\small \\trm}}}};""")
    else:
        print(f"""    \\nextgroupplot[
        yshift=1cm,
        ymin={min_}, ymax={max_},
        xticklabels={{$N$=0\\quad~~,1, 2, 3, 4, 5, 6, 7, 8, 9}},
        ytick = {{32, 33, 34, 35}}]
    \\node[] at (axis cs: .4, {max_-0.5}) {{{{\\small \\tr}}}};""")

    sign = []
    for m, rows in filtered_df.groupby(['method'])[['n', 'value']]:
        rows = rows.sort_values('n')
        rows = rows[['n', 'value', 'sign']].to_dict('split')['data']
        for n, v, s in rows:
            if s:
                sign.append((n, v))
        rows = [(0, baseline, False)] + rows

        print(f"""    \\addplot+[smooth] plot coordinates {{
        {' '.join([f'({n}, {v:.2f})' for n, v, s in rows])}}};
    \\addlegendentry{{{m}}}\n""")

    print(f"""    \\addplot[mark=none, black, dashed] coordinates {{(0, {baseline}) (9, {baseline})}};
    % baseline

    \\addplot[only marks, mark=square, color=black, thick, mark size=3pt] plot coordinates {{
        {' '.join([f'({n}, {v:.2f})' for n, v in sign])}}};
    % significative points
    """)
    if ref == 'all':
        print('    \\legend{}')

print("""    \\end{groupplot}
    \\end{tikzpicture}""")
```

