# Verification du succès de l'import dans la BDD

import re
import json
regex = re.compile(r'\),\((\d+),(\d+|NULL),\'')
data = []
with open('citations.sql') as f:
    for i, line in enumerate(tqdm(f)):
        if not line.startswith('INSERT'):
            continue
        tmp = [int(e.group(1)) for e in regex.finditer(line)]
        tmp = [line[32:60].split(',', 1)[0]] + tmp
        if tmp:
            data.append((i, tmp))

with open('ref_id_citations.json', 'w') as f:
    json.dump(data, f)

#---------------------------------------------

import json
from tqdm import tqdm
from marisa_trie import Trie

with open('ref_id_citations.json') as f:
    data = json.load(f)
data = [(i, [int(e) for e in v]) for i, v in data]

with open('tmp/ids_citations.csv') as f:
    bdd = Trie([l.strip() for l in f if l.strip()])

found = open('tmp/ids_citations_found.tmp', 'w')
not_found = []
for line_n, line_ids in tqdm(data):
    new_line_ids = []
    for id_ in line_ids:
        if str(id_) in bdd:
            found.write(f'{id_}\n')
        else:
            new_line_ids.append(id_)
    if new_line_ids:
        not_found.append((line_n, new_line_ids))
found.close()

# not_found: il faut importer ces lignes dans mysql
# Lignes de 46968 à 47013
not_found2 = {e[0]: e[1] for e in not_found}
data2 = {e[0]: e[1] for e in data}
[k for k in not_found2 if set(not_found2[k]) != set(data2[k])]
# VIDE

# found: bdd - found = les ID qui sont dans la BDD mais pas
#   dans les fichiers (le code qui extrait les ID a un soucis)
# comm -23 ids_citations.csv ids_citations_found.tmp
# VIDE


import re
import json
from tqdm import tqdm
from marisa_trie import Trie

regex = re.compile(r'\),\((\d+),\d+,\'')
data = []
with open('citationContexts.sql') as f:
    for i, line in enumerate(tqdm(f)):
        if not line.startswith('INSERT'):
            continue
        tmp = [int(e.group(1)) for e in regex.finditer(line)]
        tmp = [int(line[39:60].split(',', 1)[0])] + tmp
        if tmp:
            data.append((i, tmp))

with open('ref_id_citationContexts.json', 'w') as f:
    json.dump(data, f)

#----------------------------------

import json
from tqdm import tqdm
from marisa_trie import Trie

with open('ref_id_citationContexts.json') as f:
    data = json.load(f)
data = [(i, [int(e) for e in v]) for i, v in data]

with open('tmp/ids_citationContexts.csv') as f:
    bdd = Trie([l.strip() for l in f if l.strip()])

found = open('tmp/ids_citationContexts_found.tmp', 'w')
not_found = []
for line_n, line_ids in tqdm(data):
    new_line_ids = []
    for id_ in line_ids:
        if str(id_) in bdd:
            found.write(f'{id_}\n')
        else:
            new_line_ids.append(id_)
    if new_line_ids:
        not_found.append((line_n, new_line_ids))
found.close()

# not_found: il faut importer ces lignes dans mysql
not_found2 = {e[0]: e[1] for e in not_found}
data2 = {e[0]: e[1] for e in data}
# Est-ce qu'il y a des lignes chargées de manière incomplète ?
[k for k in not_found2 if set(not_found2[k]) != set(data2[k])]
# Non # Erreurs [14837, 18815, 19702, 19754, 19878, 36187]

# found: bdd - found = les ID qui sont dans la BDD mais pas
#   dans les fichiers (le code qui extrait les ID a un soucis)
# comm -23 ids_citationContexts.csv ids_citationContexts_found.tmp
# VIDE