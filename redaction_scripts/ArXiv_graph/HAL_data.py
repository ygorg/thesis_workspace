"""
Heavily inspired by [`esperr/med-by-year`](https://github.com/esperr/med-by-year)
"""

import os
import time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Download the file from `url` and save it locally under `file_name`:
url = "https://hal.archives-ouvertes.fr/search/index/?q=*&submit=&docType_s%5B%5D=ART&docType_s%5B%5D=COMM&docType_s%5B%5D=OUV&docType_s%5B%5D=COUV&docType_s%5B%5D=DOUV&docType_s%5B%5D=OTHER&docType_s%5B%5D=UNDEFINED&docType_s%5B%5D=REPORT&docType_s%5B%5D=THESE&docType_s%5B%5D=HDR&docType_s%5B%5D=LECTURE"
cache = 'tmp_hal.csv'
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

yearCounts = []
lab_html = BeautifulSoup(data, "html.parser")

yearfacets = lab_html.find(id='producedDateY_i-facet-content')
yearCounts = [tuple(int(i) for i in e.text[:-1].split(' ('))
              for e in yearfacets.find_all('label')]

df = pd.DataFrame(yearCounts, columns=['year', 'count'])
df = df.applymap(int)
df = df[df['year'] != df['year'].max()]
df = df[df['year'] >= 1995]

print(url)
print(''.join(map(str, df.set_index('year').to_records('list'))))

sns.set(style='whitegrid')
p = sns.lmplot(x='year', y='count', data=df, order=4)
xmin, xmax, ymin, ymax = plt.axis()
plt.text(
    xmax, ymin + 2000,
    'Source: \n{}'.format(url), color='grey', fontsize='x-small', ha='right')
plt.title('New submission per year')
plt.savefig('hal_submissions.png', bbox_inches='tight')
