# Creating the corpus

## Data

Download data from [raw refseer](https://psu.app.box.com/v/refseer).

This is 3 sql files:
- citationContexts.sql (44Go)
- citations.sql (46Go)
- papers.sql (4.5Go)

Import those into mysql (this take a **very very very** long time appr. 10Go/20h).

```sql
# This makes the process faster (though I don't know what it does)
set autocommit=0; set unique_checks=0; set foreign_key_checks=0; SET GLOBAL innodb_flush_log_at_trx_commit = 2; SET GLOBAL query_cache_type = 0; SET GLOBAL query_cache_size = 0;
```

I split the citationContexts and citations file into smaller 10,000 lines file to facilitate the process.


## SQl Query

First : select papers that are cited at least 5 times and that have a cluster (a cluster implies having citation contexts).
Second: join thoses papers with the citation contexts and output

It takes quite a while appr. 1 hour.

```sql
SELECT P.cluster, P.id, CC.id, P.year, P.title, P.abstract, CC.context
FROM citations C INNER JOIN (SELECT * FROM papers WHERE id IN (
  SELECT MAX(id) FROM (
    SELECT P.cluster, P.id
      FROM citations C INNER JOIN papers P ON C.cluster = P.cluster
                       INNER JOIN citationContexts CC on C.id = CC.citationid
      WHERE C.cluster <> 0 and CC.context <> ""
      GROUP BY P.cluster, P.id
      HAVING COUNT(CC.id) >= 5) AS tmp
	GROUP BY cluster)) AS P ON C.cluster = P.cluster
                 INNER JOIN citationContexts CC on C.id = CC.citationid
```


mysql -u admin -p citeseerx < la_requete.sql > data.csv

## Cleaning / Mapping title to search for keyword

From csv sql output to jsonl with contexts and author_keyword if available.

cat data.csv | python3 citeseer_csv2jsonl.py > data.jsonl

## Extracting keyphrases from citation contexts

From jsonl with contexts to jsonl with synth keywords

cat data.jsonl | python3 extract_kw_from_cit.py > 

## Statistics

From database (head citations.sql -n 10000): at least 5 citation context
Remove any row with empty citationid or citation context or no begining of citation marker.

To choose keywords:
- Select candidate using grammar (??)
- Keep the candidates appearing in at least 2 contexts (to do ptdr grose conne)
- Filter documents where >70% of punctuation char
- Filter candidates on (small words, punctutation/letter ratio, is citation str, special char, )

Train: 330,092
Valid: 10,000
Test: 10,000
On all with author:
- doc w/author kw : 39,245 (11.2%)
- cov of author kw using synthetic: 19.31 (15.52 test)
- cov of present author kw using present synthetic : 25.69 (21.25 test)
- cov of absent author kw using absent synthetic :  7.11 (4.87 test)
- nombre de mots en commun

On test :
- kw / doc: 26.8
- abs / kw : 79.53
- w / kws : 1.8 (author), 1.5 (synth)

train sur 10,000 documents:
      synth  author 
F@10  11.12    9.34
F@26  12.05
F@7            8.87