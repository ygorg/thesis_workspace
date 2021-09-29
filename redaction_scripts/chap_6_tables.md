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
import gzip
import pandas as pd
from tqdm import tqdm
from glob import glob
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


def extract_content(tagged_line, tag):
    """Extract content from SGML line."""
    return tagged_line.replace("<"+tag+">", "").replace("</"+tag+">","")


def compute_kw_number():
    import gzip
    import pandas as pd
    from tqdm import tqdm
    from glob import glob
    data = {}
    for file_path in tqdm(glob('/home/gallina/redefining-absent-keyphrases/data/ntcir-2/collections/*/*.gz')):
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

    return pd.DataFrame([exp_to_param(k.split(os.sep)[-2]) + [round(v, 1)] for k, v in data.items()], columns=['ref', 'method', 'n', 'prmu', 'nb_kws'])


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
# df_nb_kws = compute_kw_number()
df_nb_kws = pd.read_csv(StringIO(',ref,method,n,prmu,nb_kws\n0,none,none,none,none,0.0\n1,all,none,none,none,4.8\n2,p,none,none,none,3.1\n3,r,none,none,none,1.3\n4,m,none,none,none,1.5\n5,u,none,none,none,1.5\n6,rmu,none,none,none,2.3\n7,pr,none,none,none,3.4\n8,mu,none,none,none,2.0\n9,all,CopyRNN,5,m,6.0\n10,all,CopyRNN,5,u,6.0\n11,none,CopyRNN,5,pr,8.5\n12,none,CopyRNN,5,mu,3.9\n13,none,CopyRNN,5,rmu,6.1\n14,all,CopyRNN,5,rmu,10.7\n15,all,CorrRNN,1,none,5.7\n16,all,CorrRNN,2,none,6.7\n17,none,CorrRNN,3,none,3.0\n18,none,CorrRNN,4,none,4.0\n19,none,CorrRNN,6,none,6.0\n20,all,CorrRNN,6,none,10.7\n21,all,CorrRNN,7,none,11.7\n22,all,CorrRNN,8,none,12.7\n23,none,CorrRNN,9,none,8.9\n24,none,CorrRNN,5,p,5.0\n25,none,CorrRNN,5,r,2.6\n26,all,CorrRNN,5,r,6.7\n27,all,CorrRNN,5,m,5.1\n28,all,CorrRNN,5,u,4.9\n29,none,CorrRNN,5,pr,6.9\n30,none,CorrRNN,5,mu,1.9\n31,none,CorrRNN,5,rmu,2.9\n32,all,CorrRNN,5,rmu,7.0\n33,all,KeaOneModel,1,none,5.7\n34,none,CopyRNN,5,none,5.0\n35,all,CopyRNN,5,none,9.7\n36,none,CorrRNN,5,none,5.0\n37,all,CorrRNN,5,none,9.7\n38,none,KeaOneModel,5,none,5.0\n39,all,KeaOneModel,5,none,9.7\n40,none,MultipartiteRank,5,none,5.0\n41,all,MultipartiteRank,5,none,9.7\n42,none,TfIdf,5,none,5.0\n43,all,TfIdf,5,none,9.7\n44,none,TfIdfOneModel,5,none,5.0\n45,all,TfIdfOneModel,5,none,9.7\n46,none,CopyRNN,1,none,1.0\n47,all,CopyRNN,1,none,5.7\n48,none,CopyRNN,2,none,2.0\n49,all,CopyRNN,2,none,6.7\n50,none,CopyRNN,3,none,3.0\n51,all,CopyRNN,3,none,7.7\n52,none,CopyRNN,4,none,4.0\n53,all,CopyRNN,4,none,8.7\n54,none,CopyRNN,6,none,6.0\n55,all,CopyRNN,6,none,10.7\n56,none,CopyRNN,7,none,7.0\n57,all,CopyRNN,7,none,11.7\n58,none,CopyRNN,8,none,8.0\n59,all,CopyRNN,8,none,12.7\n60,none,CopyRNN,9,none,9.0\n61,all,CopyRNN,9,none,13.7\n62,none,CopyRNN,5,p,5.0\n63,all,CopyRNN,5,p,9.7\n64,none,CopyRNN,5,r,3.8\n65,all,CopyRNN,5,r,8.3\n66,none,CopyRNN,5,m,2.5\n67,none,CopyRNN,5,u,2.9\n68,all,CopyRNN,5,pr,13.3\n69,all,CopyRNN,5,mu,7.2\n70,none,CorrRNN,1,none,1.0\n71,none,CorrRNN,2,none,2.0\n72,all,CorrRNN,3,none,7.7\n73,all,CorrRNN,4,none,8.7\n74,none,CorrRNN,7,none,7.0\n75,none,CorrRNN,8,none,8.0\n76,all,CorrRNN,9,none,13.7\n77,all,CorrRNN,5,p,9.7\n78,none,CorrRNN,5,m,1.8\n79,none,CorrRNN,5,u,1.9\n80,all,CorrRNN,5,pr,11.6\n81,all,CorrRNN,5,mu,5.2\n82,none,KeaOneModel,1,none,1.0\n83,none,KeaOneModel,2,none,2.0\n84,all,KeaOneModel,2,none,6.7\n85,none,KeaOneModel,3,none,3.0\n86,all,KeaOneModel,3,none,7.7\n87,none,KeaOneModel,4,none,4.0\n88,all,KeaOneModel,4,none,8.7\n89,none,KeaOneModel,6,none,6.0\n90,all,KeaOneModel,6,none,10.7\n91,none,KeaOneModel,7,none,7.0\n92,all,KeaOneModel,7,none,11.7\n93,none,KeaOneModel,8,none,8.0\n94,all,KeaOneModel,8,none,12.7\n95,none,KeaOneModel,9,none,9.0\n96,all,KeaOneModel,9,none,13.7\n97,none,MultipartiteRank,1,none,1.0\n98,all,MultipartiteRank,1,none,5.7\n99,none,MultipartiteRank,2,none,2.0\n100,all,MultipartiteRank,2,none,6.7\n101,none,MultipartiteRank,3,none,3.0\n102,all,MultipartiteRank,3,none,7.7\n103,none,MultipartiteRank,4,none,4.0\n104,all,MultipartiteRank,4,none,8.7\n105,none,MultipartiteRank,6,none,6.0\n106,all,MultipartiteRank,6,none,10.7\n107,none,MultipartiteRank,7,none,7.0\n108,all,MultipartiteRank,7,none,11.7\n109,none,MultipartiteRank,8,none,8.0\n110,all,MultipartiteRank,8,none,12.7\n111,none,MultipartiteRank,9,none,9.0\n112,all,MultipartiteRank,9,none,13.7\n113,none,TfIdf,1,none,1.0\n114,all,TfIdf,1,none,5.7\n115,none,TfIdf,2,none,2.0\n116,all,TfIdf,2,none,6.7\n117,none,TfIdf,3,none,3.0\n118,all,TfIdf,3,none,7.7\n119,none,TfIdf,4,none,4.0\n120,all,TfIdf,4,none,8.7\n121,none,TfIdf,6,none,6.0\n122,all,TfIdf,6,none,10.7\n123,none,TfIdf,7,none,7.0\n124,all,TfIdf,7,none,11.7\n125,none,TfIdf,8,none,8.0\n126,all,TfIdf,8,none,12.7\n127,none,TfIdf,9,none,9.0\n128,all,TfIdf,9,none,13.7\n129,none,TfIdfOneModel,1,none,1.0\n130,all,TfIdfOneModel,1,none,5.7\n131,none,TfIdfOneModel,2,none,2.0\n132,all,TfIdfOneModel,2,none,6.7\n133,none,TfIdfOneModel,3,none,3.0\n134,all,TfIdfOneModel,3,none,7.7\n135,none,TfIdfOneModel,4,none,4.0\n136,all,TfIdfOneModel,4,none,8.7\n137,none,TfIdfOneModel,6,none,6.0\n138,all,TfIdfOneModel,6,none,10.7\n139,none,TfIdfOneModel,7,none,7.0\n140,all,TfIdfOneModel,7,none,11.7\n141,none,TfIdfOneModel,8,none,8.0\n142,all,TfIdfOneModel,8,none,12.7\n143,none,TfIdfOneModel,9,none,9.0\n144,all,TfIdfOneModel,9,none,13.7\n'))
df = pd.merge(df, df_nb_kws)
#df = df.melt(set(df.columns) - set(['score', 'diff', 'nb_kws']))
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
prmu_full_lst = ['p', 'r', 'm', 'u', 'rmu', 'pr', 'mu', 'none']
prmu_full_lst = ['none', 'pr', 'mu']
method_full_lst = ['CorrRNN', 'CopyRNN']
prmu2latex = {'p': '\\present', 'r': '\\reordonne', 'm': '\\mixte', 'u': '\\nonvu', 'none': 'P+R+M+U', 'rmu': 'Absent (RMU)', 'pr': 'Highlight (P+R)', 'mu': 'Expand (M+U)'}

# Predicted KW version
prepare_df = lambda df: df.melt(set(df.columns) - set(['score', 'diff', 'nb_kws'])).groupby(['method', 'prmu', 'variable', 'system', 'ref', 'collection']).apply(lambda x: x.to_dict('records')).apply(stylee).unstack().unstack().unstack().unstack()

baseline = prepare_df(df[df['system'].isin(['bm25', 'bm25+rm3'])][df['method'] == 'none'][df['ref'].isin(['none', 'all'])]).rename(index={'none': '-'}, level=0)


pred_ = prepare_df(df[df['system'].isin(['bm25', 'bm25+rm3'])][df['n']=='5']).reindex(prmu_full_lst, level=1).rename(index=prmu2latex, level=1).reindex(method_full_lst, level=0)

out = pd.concat([baseline, pred_]).reindex(['score', 'nb_kws'], axis=1, level=3).reindex(['none', 'all'], axis=1, level=1).rename(columns={'none': '\\tr', 'all': '\\trm'}, level=1).reindex(['bm25+rm3'], axis=1, level=2)

print(out.to_latex(escape=False, multicolumn_format='c', label=f'prmu_pred_{method.lower()}', caption=method))
```

## Tableau prmu_ref

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
