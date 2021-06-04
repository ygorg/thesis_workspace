import os
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from urllib.request import urlopen

# Download the file from `url` and save it locally under `file_name`:
url = 'https://arxiv.org/stats/get_monthly_submissions'
cache = 'tmp_arxiv.csv'
try:
    if time.time() - os.path.getmtime(cache) > 3600 * 24:
        raise FileNotFoundError
    with open(cache, 'r') as f:
        data = f.read()
    print('Using cached version')
except FileNotFoundError:
    with urlopen(url) as response:
        data = response.read()  # a `bytes` object
        encoding = response.info().get_param('charset', 'utf-8')
    data = data.decode(encoding)
    print('Downloading')
    with open(cache, 'w') as f:
        f.write(data)
    print('Saving to cache')

df = pd.read_csv(cache)
df['year'] = df['month'].apply(lambda x: int(x[:4]))
df = df[df['year'] != df['year'].max()]

per_year = df.groupby('year')['submissions'].sum().reset_index()

print(url)
print(''.join(map(str, per_year.set_index('year').to_records('list'))))


sns.set(style='whitegrid')
p = sns.lmplot(x='year', y='submissions', data=per_year, order=4)
xmin, xmax, ymin, ymax = plt.axis()
plt.text(
    xmax, ymin + 2000,
    'Source: \n{}'.format(url), color='grey', fontsize='x-small', ha='right')
plt.title('New submission per year')
plt.savefig('arxviv_submissions.png', bbox_inches='tight')
