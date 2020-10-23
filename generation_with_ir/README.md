# Données de contextes de citation:

Chercher des graphes de citation pour avoir les identifiants de l'article cité et citant !

Si un article A (citant) cite un article B (cité).
J'ai besoin de la notice de l'article B (cité) et du contexte de citation de l'article A (citant).

Manque termes-clés
Littéralement ce dont j'ai besoin [scite_](https://scite.ai/)

Parse scientific articles:
https://github.com/allenai/science-parse
https://github.com/allenai/spv2
https://github.com/kermitt2/grobid

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
set autocommit=0; set unique_checks=0; set foreign_key_checks=0; SET GLOBAL innodb_flush_log_at_trx_commit = 2; SET GLOBAL query_cache_type = 0; SET GLOBAL query_cache_size = 0;

SELECT P.cluster, P.id, CC.id, P.year, P.title, P.abstract, CC.context
FROM citations C INNER JOIN (SELECT * FROM papers WHERE id IN (
  SELECT MAX(id) FROM (
    SELECT P.cluster, P.id
      FROM citations C INNER JOIN papers P ON C.cluster = P.cluster
                       INNER JOIN citationContexts CC on C.id = CC.citationid
      WHERE C.cluster <> 0
      GROUP BY P.cluster, P.id
      HAVING COUNT(CC.id) >= 5) AS tmp
	GROUP BY cluster)) AS P ON C.cluster = P.cluster
                 INNER JOIN citationContexts CC on C.id = CC.citationid
LIMIT 10;

# Les documents qui sont ok
SELECT MAX(id) FROM
	(SELECT P.cluster, P.id
	 FROM citations C INNER JOIN papers P ON C.cluster = P.cluster
					  INNER JOIN citationContexts CC on C.id = CC.citationid
	 WHERE C.cluster <> 0
	 GROUP BY P.cluster, P.id
	 HAVING COUNT(CC.id) >= 5) AS tmp
GROUP BY cluster
```

https://www.sciencedirect.com/science/article/pii/S0375947405001788/pdfft

### Semantic Scholar [s2orc](https://github.com/allenai/s2orc/)
- Source: SemanticScholar
- Domaine: -
- Documents: ~12M de doc full text
- Liens: ?
- Doc avec arc entrant: ?
- Keyword: full_text ?

- API: [non parsé](http://s2-public-api-prod.us-west-2.elasticbeanstalk.com/corpus/)

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

### [OAG](https://www.openacademic.ai/oag/)
- Source: AMiner / MAG
- Domaine: -
- Documents: 208M+172M
- Liens: 91M
- Doc avec arc entrant: ?
- Keyword: AMiner 9Go / 139Go : 50% de couverture (total ?)

- Full-text: AMiner 9Go/139Go : 0.3%

[MAG - table references](https://docs.microsoft.com/en-us/academic-services/graph/reference-data-schema)


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






with open('data.csv', 'rb') as f: 
    weird_shit = [] 
    g = open('data.jsonl', 'w') 
    columns = f.readline().encode('utf-8').strip().split('\t') 
    columns[1] = 'papers_id' 
    columns[2] = 'citationcontext_id' 
    #f = map(lambda l: l.strip().split('\t'), f) 
    line = next(f, None).encode('utf-8') 
    line_acc = line.replace('\n', ' ') 
    cur_j = None 
    cur_c = None 
    ctx_acc = [] 
    i = 1 
    while line: 
        line = next(f, None).encode('utf-8') 
        i += 1 
        if not re.match(r'\d+\t\d+(\.\d+)+\t\d+\t', line): 
            # Not a new row :'( 
            line_acc += line.replace('\n', ' ') 
            continue 
        # New row !! 
        l = line_acc.strip().split('\t', 4) 
        if '=-=' not in l[-1]: 
            print(i, l) 
        lc, rc = l[-1].split('=-=') 
        a, lc = lc.rsplit('\t', 1) 
        l = l[:-1] + a.split('\t') + [lc + '=-=' + rc] 
         
        line_acc = line 
        if len(l) != len(columns): 
            # Row with extra \t :'( 
            weird_shit.append(l) 
            print(l) 
            print(i, len(l), len(columns)); input() 
            continue 
        if cur_c is None: 
            cur_c = l[0] 
        if cur_j is None: 
            cur_j = {columns[i]: l[i] for i in [0,1,3,4,5]} 
         
        if cur_c == l[0]: 
            # Same cluster :'( 
            acc.append((l[2], l[-1])) 
            continue 
        # New cluster ! 
        if cur_c is not None: 
            cur_j['ctxt'] = acc 
            g.write(json.dumps(cur_j) + '\n') 
        acc = [(l[2], l[-1])] 
        cur_j = {columns[i]: l[i] for i in [0,1,3,4,5]} 
        cur_c = l[0] 
    g.close()