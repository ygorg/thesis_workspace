import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_csv('reported_scores.csv')
df['metric2'] = df['metric'].apply(lambda x: x.replace('A ', '').replace('P ', ''))
df['score'] = df['score'].apply(lambda x: x.replace(',', '.')).apply(float)

# How many method per dataset/metric ?
tmp = df[['metric2', 'dataset', 'method']].drop_duplicates().groupby(['metric2', 'dataset']).count().unstack()
tmp.loc[tmp.sum(1).sort_values().index[:-25:-1],tmp.sum().sort_values().index[:-23:-1]]

# Mean of everything
df.groupby(['year', 'method', 'end2end'])['score'].agg(['mean']).reset_index(['year', 'end2end']).plot.scatter(x='year', y='mean', c='end2end', colormap='viridis')
plt.show()

# Mean of 'All metrics' if more than 10 datapoints
aa = df[(df['filter'] == 'All')].groupby(['year', 'method', 'end2end'])['score'].agg(['mean', 'count'])
aa[aa['count'] >= 10].reset_index(['year', 'end2end']).plot.scatter(x='year', y='mean', c='end2end', colormap='viridis')
plt.show()
meth = [
    'Tf-Idf',
    'FirstPhrases',
    'Kea',
    'TextRank',
    'SingleRank',
    'KpMiner',
    'TPR',
    'TopicRank',
    'CopyRNN',
    'PositionRank',
    'CorrRNN',
    'EmbedRank',
    'catSeqD',
    'catSeqTG-2RF1',
    'Transformer',
    'YAKE',
    'SEG-Net']

# Fixing dataset and metric using same method subset as "" Mean of 'All metrics' if more than 10 datapoints ""
df[(df['big study'] == 'FAUX') & (df['method'].isin(meth))
   & (df['dataset'] == 'SemEval-2010') & (df['metric'] == 'P F@5')]\
    .groupby(['method']).agg({'score': 'mean', 'end2end': 'max', 'year': 'max'})\
    .sort_values(['end2end', 'year']).round(2)\
    .reset_index()[['year', 'score', 'end2end', 'method']].to_csv(index=False, sep=' ')



# Compute a fake 'all score' if prs+abs are available

# From Gallina, 2020
abs_ratio = {
    'Inspec': 22.4,
    'KP20k': 42.6,
    'ACM': 16.3,
    'NUS': 14.4,
    'SemEval-2010': 19.7
}


for k, v in df[df['filter'] != 'All'].groupby(['dataset', 'method', 'metric2'])[['filter', 'score']]:
    p = v[v['filter'] == 'Prs']
    a = v[v['filter'] == 'Abs']
    if len(p) > 0 and len(a) > 0:
        new_score = ((1-abs_ratio[k[0]]/100) * p.mean() + abs_ratio[k[0]]/100 * a.mean()).values[0]
        print(';'.join(['fake', k[1], '', k[0], k[2], 'All', f'{new_score:.2f}'.replace('.', ','), 'FAUX', '1', 'interpolation scores prs/abs avec %d\'abs']))
