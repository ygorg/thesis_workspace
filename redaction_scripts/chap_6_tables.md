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
    for METH in "MultipartiteRank" "CorrRNN" "CopyRNN"
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
import pandas as pd
from glob import glob
from scipy import stats


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


def param_to_file(coll, sys_, r, m, n, p):
    if m and not n or p and not m:
        raise ArgumentError()
    tmp = []
    if r:
        tmp += [r]
    if m:
        tmp += [m, n]
        if p:
            tmp += [p]
    if tmp:
        tmp = '-' + '-'.join(tmp)
    else:
        tmp = ''

    return f'/home/gallina/redefining-absent-keyphrases/data/{coll}/output/run.{coll}-t+a{tmp}.description.{sys_}.results'


def file_to_param(f):
    coll = f.split(os.sep)[-3]
    exp, _, sys_ = os.path.basename(f).split('.')[1:4]
    exp_ = exp.split('-')[3:]
    if not exp_:
        exp_ = ['none'] * 4
    elif exp_[0][0].islower():
        # there are reference keyphrases
        exp_ += ['none'] * (4 - len(exp_))
    else:
        # there are reference keyphrases
        exp_ = ['none'] + exp_ + ['none'] * (3 - len(exp_))
    r, m, n, p = exp_
    return coll, sys_, r, m, n, p


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

files = glob('/home/gallina/redefining-absent-keyphrases/data/ntcir-2/output/*.results')

data = []
for f in files:
    coll, sys_, r, m, n, p = file_to_param(f)
    s = load_scores(f)
    s.pop('all')
    mean_s = mean(s.values()) * 100

    s_baseline = load_scores(param_to_file(coll, sys_, None if r == 'none' else r, None, None, None))
    s_baseline.pop('all')
    mean_s_baseline = mean(s_baseline.values()) * 100

    tmp_keys = list(s_baseline)
    ttest = stats.ttest_rel(a=[s[k] for k in tmp_keys], b=[s_baseline[k] for k in tmp_keys])[1]
    sign = ttest < .05

    data.append([coll, r, m, n, p, sys_, mean_s, sign, mean_s - mean_s_baseline, f])

df = pd.DataFrame(data, columns=['collection', 'ref', 'method', 'n', 'prmu', 'system', 'score', 'sign', 'diff', 'file_path'])
df = df.melt(set(df.columns) - set(['score', 'diff']))
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


## Tableau full_retrieval_results

```python
prmu_full_lst = ['p', 'r', 'm', 'u', 'rmu', 'pr', 'mu', 'none']
prmu2latex = {'p': '\\present', 'r': '\\reordonne', 'm': '\\mixte', 'u': '\\nonvu', 'none': 'P+R+M+U', 'rmu': 'Absent (RMU)', 'pr': 'Highlight (P+R)', 'mu': 'Expand (M+U)'}

# Predicted KW version
prepare_df = lambda df: df.groupby(['prmu', 'variable', 'system', 'ref', 'collection']).apply(lambda x: x.to_dict('records')).apply(stylee).unstack().unstack().unstack().unstack()

baseline = prepare_df(df[df['system'].isin(['bm25', 'bm25+rm3'])][df['method'] == 'none'][df['ref'].isin(['none', 'all'])]).rename(index={'none': '-'})

method = 'CopyRNN'
pred_ = prepare_df(df[df['system'].isin(['bm25', 'bm25+rm3'])][df['method'] == method][df['n']=='5']).reindex(prmu_full_lst).rename(index=prmu2latex)

out = pd.concat([baseline, pred_]).reindex(['score', 'diff'], axis=1, level=3).reindex(['none', 'all'], axis=1, level=1).rename(index={'none': '\\tr', 'all': '\\trm'}, level=1)

print(out.to_latex(escape=False, multicolumn_format='c', label=f'prmu_pred_{method.lower()}', caption=method))
```

```python
# Reference KW version
prepare_df = lambda df: df.groupby(['ref', 'variable', 'system', 'collection']).apply(lambda x: x.to_dict('records')).apply(stylee).unstack().unstack().unstack()

ref = prepare_df(df[df['variable'] == 'score'][df['system'].isin(['bm25', 'bm25+rm3'])][df['method'] == 'none']).reindex(prmu_full_lst).rename(index=prmu2latex)

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

print("""
    \\begin{tikzpicture}[trim axis left,trim axis right]
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
    filtered_df = df[df['variable'] == 'score'][df['system'] == 'bm25+rm3'][df['ref'] == ref][df['method'].isin(['CopyRNN', 'CorrRNN', 'MultipartiteRank', 'KeaOneModel'])][df['prmu'] == 'none']

    baseline = df[df['variable'] == 'score'][df['system'] == 'bm25+rm3'][df['ref'] == ref][df['method'] == 'none']
    assert len(baseline) == 1

    baseline = baseline['value'].values[0]

    if ref == 'none':
        print("""
    \\nextgroupplot[
        ymin=34.75, ymax=38,
        xticklabels={,,,},
        ytick = {35, 36, 37}]
    \\node[] at (axis cs: .4, 37.5) {{{{\\small \\tr}}}};""")
    else:
        print("""
    \\nextgroupplot[
        ymin=32.25,ymax=36,
        xticklabels={$N$=0\\quad~~,1, 2, 3, 4, 5, 6, 7, 8, 9},
        ytick = {32, 33, 34, 35}]
    \\node[] at (axis cs: .4, 37.5) {{{{\\small \\trm}}}};""")

    sign = []
    for m, rows in filtered_df.groupby(['method'])[['n', 'value']]:
        rows = rows.sort_values('n')
        rows = rows[['n', 'value', 'sign']].to_dict('split')['data']
        for n, v, s in rows:
            if s:
                sign.append((n, v))
        rows = [(0, baseline, False)] + rows

        print(f"""
    \\addplot+[smooth] plot coordinates {{
        {' '.join([f'({n}, {v:.2f})' for n, v, s in rows])}}};
    \\addlegendentry{{{m}}}\n""")

    print(f"""
    \\addplot[mark=none, black, dashed] coordinates {{(0, {baseline}) (9, {baseline})}};
    % baseline

    \\addplot[only marks, mark=square, color=black, thick, mark size=3pt] plot coordinates {{
        {' '.join([f'({n}, {v:.2f})' for n, v in sign])}}};
    % significative points
    """)

print("""
    \\end{{groupplot}}
    \\end{{tikzpicture}}""")
```
