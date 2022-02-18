wget "https://aclanthology.org/anthology.bib.gz"
zcat "anthology.bib.gz" | grep "year = " | sed -E 's/    year = "([0-9]+)",/\1/g' | sort | uniq -c | sed 's/^ *//g' | tail -n 30


# for acmdl
# request: "result OR abstract OR introduction OR study OR work OR present OR paper OR experiment OR method OR author OR this OR investigate OR science OR travaux OR computer"
# returns ~90% of all documents. Then this JS code returns the nb of doc per year
"""
var total = parseInt(document.getElementsByClassName('hitsLength')[0].textContent.replaceAll(',', ''));
var data = JSON.parse(document.getElementsByClassName('facetDateChart')[0].getAttribute('data-yearweights'));
var yearmin = parseInt(document.getElementsByClassName('facetDateChart')[0].getAttribute('data-min'));
/* data is between 0 and 1, with 1 having the most doc per year.
These numbers need to be transformed in number of document.*/
var coef = total*1/data.reduce((acc, v) => acc + v, 0);
var out = '';
for (var i = 0; i < data.length; i++) {
  out += '(' + (yearmin+i) + ', ' + (Math.round(data[i]*coef)) + ')';
}
console.log(out);
"""