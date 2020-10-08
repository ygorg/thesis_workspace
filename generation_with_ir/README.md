# Données de contextes de citation:

Chercher des graphes de citation pour avoir les identifiants de l'article cité et citant !

Si un article A (citant) cite un article B (cité).
J'ai besoin de la notice de l'article B (cité) et du contexte de citation de l'article A (citant).

### Acl Anthology Network [AAN](http://aan.how/)
- Source: ACL Anthology
- Domaine: Natural Language Processing
- Documents: 23,595
- Liens: 604,090
- Doc avec arc entrant: 13,674
- Keyword: fulltext ?

- Doc avec citation summary (précalculé): 5,914

### [RefSeerX](https://github.com/tebesu/NeuralCitationNetwork)
- Source: CiteSeerX
- Domaine: -
- Documents: 5,334,095 (4,510,727 cluster)
- Liens: 25,302,904 (21% de la table chargée pour l'instant)
- Document avec arc entrant: ?
- Keyword: non
- Contextes de citation: 105,337,269

Notice citante + contexte de citation citant + Notice article cité

```sql
SELECT P.cluster, P.id, CC.id, P.year, P.title, P.abstract, CC.context
FROM citations C INNER JOIN papers P ON C.cluster = P.cluster
			  	 INNER JOIN citationContexts CC on C.id = CC.citationid
LIMIT 10;
```

### Semantic Scholar [s2orc](https://github.com/allenai/s2orc/)
- Source: SemanticScholar
- Domaine: -
- Documents: ~12M de doc full text
- Liens: ?
- Doc avec arc entrant: ?
- Keyword: full_text ?

```python
with open('metadata.jsonl') as f:
    meta_ids = []
    for l in map(json.loads, f):
        if l['has_pdf_parse'] and l['has_pdf_parsed_bib_entries'] and l['has_pdf_parsed_bod_text']:
            meta_ids.append(l['paper_id'])

with open('pdf_parses.jsonl') as f:
	papers = [p for p in map(json.loads, f) if p['paper_id'] in meta_ids]

for p in papers:
	refs = [[c['ref_id'] for c in s['cite_spans']] for s in p['body_text'] if s['cite_spans']]
	[p['bib_entries'][r] for r in set(r for l in refss for r in l) if p['bib_entries'][r]['link']]

```

### [htp-th](https://research.cs.cornell.edu/kddcup/datasets.html)
- Source: ArXiV
- Domaine : high-energy physics theory
- Documents: 29,555
- Liens: 352,807
- Doc avec arc entrant: 23,180
- Keyword: full-text ?

Articles plein + lien de citation + notices
Bibliographie
Lien vers l'article cité
Contexte de citation a trouver grâce à l'article plein et le nom de l'article.

```python
def full_text(paper_id):
	with open(f'hep-th-2003/{paper_id}') as f:
		return f.read()

def title(paper_id):
	with open(f'hep-th-abs/{paper_id}') as f:
		return [l for l in f if 'title' in l.lower()][0]

def search_bibentry(full_text, title)
	pass

with open('hep-th-citations') as f:
	for line in f:
	    id_citing, id_cited = line.split(' ')
	    full_text_citing = full_text(id_citing)
	    bib_name = search_bibentry(title(id_cited))
	    for match in re.findall(
	    		'\\cite\w?{([-a-z_0-9]+,)*{}(,[-a-z_0-9]+)*}'.format(
	    			bib_name)):
	        full_text_citing[match.begin-100:match_end+100]
```

### [dblp](https://www.aminer.org/citation)
- Source: dblp
- Domaine: -
- Documents: 4,894,081
- Liens: 45,564,149
- Doc avec arc entrant: ?
- Keyword: 7,196

Notice + id reference + lien 

```python
with open('dblp.v12.json') as f:
    for line in tqdm(f):
        line = line.strip()
        if len(line) == 1:
            continue
        if line[0] == ',':
            line = line[1:]
        if line[-1] == ',':
            line = line[:-1]
        line = json.loads(line)
```

### [ISTEX](https://api.istex.fr/ark:/67375/GT4-FJLCPBW9-Q/fulltext.tei)
- Manque Identifiant pour les papiers cités.
- Article plein + contexte de citation + bibliographie

### Bibliographic Citation Recommandation Dataset [BCR](https://www.isical.ac.in/~irlab/bcr.html)
Notice citante + contexte de citation citant + Nom article cité