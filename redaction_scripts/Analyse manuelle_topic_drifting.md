# Analyse manuelle


On prend comme exemple la requête 146 qui parle de "DNA computer". Cette requête obient de moins bon résultats lorsque l'on ajoute des mots-clés aux documents.
une explication peut être le topic drifting.
Le topic drift est un phénomène qui interveint dans les systèmes itératifs.
Ici nous ajoutons des mots-clés, qui ensuite influent sur l'expansion de requête, qui influe sur le résultat final.
Nous avons donc 2 étapes.
Nous essayons de mettre à jour le fait que les mots-clés ajoutés peuvent orienter l'expansion de rqueête (RM3) dans une autre direction que la requête originale.
La requête originale est composée de 3 termes (architectur, comput et dna) les documents pertinent sot tout les document discutant de systèmes informatiques solvant des probèmes grâce à des séquences d'ADN. L'architecture (de batiments) et l'architcture d'ordinateur n'est ici pas pertinent. Les deux termes principaux de cette requête sont 'dna' et 'comput'.

L'expansion de requête RM3 se fait en ajoutant les termes les plus saillants dans les 10 premiers documents retournés par la requête originale.
Pour comprendre pourquoi l'ajout de MC aux documents à fait baisser les scores nous cherchons à savoir pourquoi les documents retournés pertinent retournés à la fin sont moins bien classé qu'avant.
Pour cela nous devons investiguer le processus d'expansion de la requête et comment l'ajout de mots-clés l'a influé.

Les termes ajoutés par RM3 dans l'indexation t+a-all-Corr et t+a-all ne différe que de 2 termes.
['core', 'problem'] pour -all et ['aid', 'network'] pour -all-Corr, ces termes ne sont pas directement lié aux thèmes de la requête.
Mais l'ajout des termes 'core' et 'problem' donnent de meilleurs résultats.
Cela veut donc dire que les documents pertinent pour cette requête ont plus de chance de contenir 'core' et/ou 'problem' ou au contraire que les documents non pertinent ont plus de chance de contenir 'aid' et/ou 'problem'. 



## Requête
```xml
<num> Number: 146
<title>DNA computer

<desc> Description:
Architecture of the DNA computer

<narr> Narrative:
In recent years, the use of DNA computers has been advocated. A DNA computer is a problem-solving system using DNA sequences in areas such as a solution of the Hamilton problem suggested by Adleman. Solutions for specific problems in other areas have also been suggested. This search request demands articles concerned with DNA computer-like systems that involve applications of the chemical action and reaction of DNA. Articles that discuss RNA computing are considered to be relevant. Articles that deal with suggestion of executable experiments not in fact executed are also considered to be relevant. Articles that discuss simulations are considered to be relevant.
```
### Termes de la requête : ['architectur', 'comput', 'dna']

`'data/ntcir-2/output/run.ntcir-2-t+a-all-CorrRNN-5.description.qld+rm3.results'`

#### SANS mots-clés
6/10 lié à la requête (5/10 relevant par qrel) document utilisés pour RM3
Termes ajoutés: ['core', 'problem', 'parallel', 'educ', 'field', 'processor', 'research']

#### AVEC mots-clés
4/10 lié à la requête (4/10 relevant par qrel) Document utilisés pour RM3
Termes ajoutés: ['aid', 'network', 'parallel', 'educ', 'field', 'processor', 'research']



# Comment le RM3 a été calculé ?

CLEAN : 6/10 socuments lié à la requête (5/10 relevant par qrel)
CORR : 4/10 documents lié à la requête (4/10 relevant par qrel)
Donc potentiellement `2*len(doc)` termes pas liés à la requête


Entre les doc utilisés pour calculer RM3 de CLEAN et CORR:
Il y a 7 doc en commun
CORR: 3 doc qui parlent d'informatique

CLEAN: 1 doc qui parle d'informatique
2 doc qui parlent de DNA computing


# Pourquoi ces 3 documents qui parlent d'informatique sont remontés ??
Les documents qui parlent de DNA computing ont été overshadowed par des documents qui parlent de architecture et d'ordinateurs car 

## Annotation "mots-clés aidant la requête"
On regarde quels mots-clés sont liés à a requête ou pas dans les mots-clés des 10 premiers documents retourné par BM25.
- Pour dire qu'un mot clé aide la requête il faut qu'il ne soit pas lié à l'informatique général et qu'il ai un lien avec l'ADN
- "Genetic algorithm" apparait seulement dans des documents pertinent mais est trop lié au domaine de l'apprentissage machine et pas assez dans le domaine de l'ADN.
- `good_kws = {'directed hamilton path problem','dna analysis','dna computation','dna computing','genome informatics','hybridization','molecular biology','molecular computing','nanotechnology','dna','genetic','hamiltonian','hamiltonian path','chromosomr sorter','dna computer','dna probe','dna sequencing','fluorescence profile','hybirdization','oligonucleotides','sbh method'}`


### %MC/doc lié à la requête
`sum(sum(k in good_kws for k in kr+kp)/len(kr+kp) for i, (t, a, kr, kp) in kws_first_docs.items())/len(kws_first_docs)`
CORR:  26.2%
CLEAN: 43.0%


CorrRNN ajoute des mots-clés selon son apprentissage, pour des documents qui parlent de adn et d'ordinateur. Il a été appris plus sur des doc qui parlent d'ordinateurs ?? Il a considéré que le thème de ce doc est les ordinateurs. Donc il génére une majorité de MC d'ordinateurs.

### %MC/doc lié à la requeête en fonction de si le  document est pertinent ou non
On considére "kaken-e-1419561700" comme pertinent.
sum(sum(k in good_kws for k in kr+kp)/len(kr+kp) for i, (t, a, kr, kp) in kws_first_docs.items() if i in qrel[req] + ['kaken-e-1419561700'])/sum(i in qrel[req] + ['kaken-e-1419561700'] for i in kws_first_docs), sum(sum(k in good_kws for k in kr+kp)/len(kr+kp) for i, (t, a, kr, kp) in clean_first_docs.items() if i in qrel[req] + ['kaken-e-1419561700'])/sum(i in qrel[req] + ['kaken-e-1419561700'] for i in clean_first_docs), sum(sum(k in good_kws for k in kr+kp)/len(kr+kp) for i, (t, a, kr, kp) in kws_first_docs.items() if not i in qrel[req] + ['kaken-e-1419561700'])/sum(i not in qrel[req] + ['kaken-e-1419561700'] for i in kws_first_docs), sum(sum(k in good_kws for k in kr+kp)/len(kr+kp) for i, (t, a, kr, kp) in clean_first_docs.items() if not i in qrel[req] + ['kaken-e-1419561700'])/sum(i not in qrel[req] + ['kaken-e-1419561700'] for i in clean_first_docs)

sum(sum(k in good_kws for k in kr)/len(kr) for i, (t, a, kr, kp) in kws_first_docs.items() if i in qrel[req] + ['kaken-e-1419561700'])/sum(i in qrel[req] + ['kaken-e-1419561700'] for i in kws_first_docs), sum(sum(k in good_kws for k in kr)/len(kr) for i, (t, a, kr, kp) in clean_first_docs.items() if i in qrel[req] + ['kaken-e-1419561700'])/sum(i in qrel[req] + ['kaken-e-1419561700'] for i in clean_first_docs), sum(sum(k in good_kws for k in kr)/len(kr) for i, (t, a, kr, kp) in kws_first_docs.items() if not i in qrel[req] + ['kaken-e-1419561700'])/sum(i not in qrel[req] + ['kaken-e-1419561700'] for i in kws_first_docs), sum(sum(k in good_kws for k in kr)/len(kr) for i, (t, a, kr, kp) in clean_first_docs.items() if not i in qrel[req] + ['kaken-e-1419561700'])/sum(i not in qrel[req] + ['kaken-e-1419561700'] for i in clean_first_docs)

sum(sum(k in good_kws for k in kp)/len(kp) for i, (t, a, kr, kp) in kws_first_docs.items() if i in qrel[req] + ['kaken-e-1419561700'])/sum(i in qrel[req] + ['kaken-e-1419561700'] for i in kws_first_docs), 0, sum(sum(k in good_kws for k in kp)/len(kp) for i, (t, a, kr, kp) in kws_first_docs.items() if not i in qrel[req] + ['kaken-e-1419561700'])/sum(i not in qrel[req] + ['kaken-e-1419561700'] for i in kws_first_docs), 0



KR+KP | pert  | non pert |
CORR  | 65.4% |     0.0% |
CLEAN | 71.8% |     0.0% |

KR    | pert  | non pert |
CORR  | 77.5% |     0.0% | 4 6
CLEAN | 71.8% |     0.0% | 6 4

KP    | pert  | non pert |
CORR  | 60.0% |     0.0% |
CLEAN |  0.0% |     0.0% |

Il ya peut-être plus de mots-clés pertinent pour les documents pertinent prédit.



### Termes de RM3 et documents
Les termes ajoutés par RM3 n'ont pas l'air intéréssant, mais ces termes apparraisent dans les doc pertinents.
Dans cb de doc les mots ajoutés apparraissent les termes ajoutés par RM3 (CORR['aid', 'network'], CLEAN['core', 'problem']) ?
`{d: [(t, f) for t, f in Counter(' '.join([t,a,' '.join(kr),' '.join(kp)]).lower().split(' ')).items() if any(t.startswith(myterm) for myterm in ['aid', 'network', 'core', 'problem'])] for d, (t, a, kr, kp) in list(kws_first_docs.items())}`
import nltk
import string
stem = nltk.porter.PorterStemmer().stem
lts = lambda x: [stem(w) for w in nltk.word_tokenize(x.lower())]
sw = nltk.corpus.stopwords.words('english')
sw += string.punctuation
{d: Counter([w for w in lts(' '.join([t,a,' '.join(kr),' '.join(kp)])) if w not in sw]).most_common(5) for d, (t, a, kr, kp) in list(kws_first_docs.items())}


tmp = [Counter([w for w in lts(' '.join([t,a,' '.join(kr),' '.join(kp)])) if w not in sw]).most_common(10) for d, (t, a, kr, kp) in list(kws_first_docs.items())]
Counter(w for d in tmp for w, f in d)


Counter(w for d, (t, a, kr, kp) in kws_first_docs.items() for w in lts(' '.join([t,a,' '.join(kr),' '.join(kp)])) if w not in sw)



10 premiers documents retournés avec BM25
CLEAN
{'kaken-e-1529529700': [('aid', 13)],
 'gakkai-e-0001653826': [('problem', 1)],
 'kaken-e-1229529600': [('core', 2), ('network', 1)],
 'gakkai-e-0001583362': [('problem', 3)],
 'kaken-e-1229770400': [('problem', 1), ('network', 2)],
 'gakkai-e-0001164387': [('problem', 1)],
 'kaken-e-1419561700': [('problem', 1)],
 'gakkai-e-0000134747': [],
 'gakkai-e-0001513382': [('problem', 1)],
 'gakkai-e-0001913223': [('problem', 4)]}

KWS
{'kaken-e-1529529700': [('aid', 15)],
 'gakkai-e-0001653826': [('problem', 1)],
 'gakkai-e-0001583362': [('problem', 4)],
 'gakkai-e-0001513382': [('problem', 1)],
 'gakkai-e-0001164387': [('problem', 1)],
 'gakkai-e-0000134747': [],
 'gakkai-e-0000159652': [],
 'gakkai-e-0000198040': [('network', 9)],
 'kaken-e-1229529600': [('core', 2), ('network', 1)],
 'gakkai-e-0000128800': []}
