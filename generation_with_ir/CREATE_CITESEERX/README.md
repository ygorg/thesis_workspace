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

First : select papers that are cited at least 5 times and that have a cluster.
Second: join thoses papers with the citation contexts and output

It takes quite a while appr. 1 hour.

```sql
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
```

## Cleaning / Mapping title to search for keyword

python3 csv2jsonl.py

## Extracting keyphrases from citation contexts