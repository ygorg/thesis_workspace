#htlatex main.tex 'xhtml,charset=utf-8' ' -cunihtf -utf8 -cvalidate' "" -shell-escape

import re
import bs4
import json

with open('main.html', encoding='utf-8') as f:
    soup = bs4.BeautifulSoup(f, 'html5lib')

[e.decompose() for e in soup.find_all('img')]
[e.decompose() for e in soup.find_all(class_='figure')]
[e.decompose() for e in soup.find_all(class_='footnote-mark')]
[e.decompose() for e in soup.find_all(class_='float')]
[e.decompose() for e in soup.find_all(class_='equation')]
[e.decompose() for e in soup.find_all(class_='gather')]
[e.decompose() for e in soup.find_all(class_='align')]

trr = {"ﬁ": "fi",
"ﬀ": "ff",
"ﬃ": "ffi",
"ﬂ": "fl",
"œ": "oe",
"“": '"',
"”": '"',
"‘": "'",
"’": "'",
"…": "...",
'«': '"',
'»': '"',
'†': '',
'|': '',
'–': '-',
'≃': '=',
'−': '-',
'∕': '/',
'𝒳': '',
'∑': '',
'∪': '',
'⌈': '',
'𝜃': '',
'ℒ': '',
'$': '',
'⋂': '',
'*': '',
'_': '',
'∏': '',
'⌋': '',
'⌉': '',
}


acc = [[]]
for e in soup.body:
    if isinstance(e, bs4.NavigableString) and not e.strip():
        continue
    if isinstance(e, bs4.Comment):
        continue
    tmp = re.sub('\s{2,}', ' ', e.text.replace('\xa0', ' ')).strip()
    for k, v in trr.items():
        tmp = tmp.replace(k, v)
    if isinstance(e, bs4.Tag) and e.name in ['h2', 'h3']:
        acc.append([])
    if e.name[0] == 'h':
        tmp += '.'
    if not tmp:
        continue
    acc[-1].append(tmp)

acc = [''.join(c) for c in acc][3:]

for i, c in enumerate(acc):
    with open(f'chap{i}.txt', 'w') as f:
	    f.write(c)

import pke
for c in acc:
	e = pke.unsupervised.MultipartiteRank()
	e.load_document(c, language='fr')
	e.candidate_selection()
	#e.candidate_filtering()
	e.candidate_weighting()
	print([k for k, s in e.get_n_best(5, redundancy_removal=True)])


e = pke.unsupervised.MultipartiteRank()
e.load_document(' '.join(acc), language='fr')
e.candidate_selection()
e.candidate_weighting()
print(e.get_n_best(20, redundancy_removal=True))


[
1:[('documents scientifiques', 0.05920445160785726), ('mots-clés', 0.04546231929162586), ('premières méthodes', 0.03348222226130807), ('chapitre 1introduction', 0.023634179411825124), ('production automatique', 0.021443880651649382), ('recherche documentaire', 0.01978786864801629), ('données différentes', 0.01599622422598717), ('concepts', 0.011707064061823553), ('évaluation usuelle compare', 0.01053725930514218), ('cadres expérimentaux différents', 0.010449824615136428), ('performances', 0.010427799928167244), ('nombre', 0.010107059310993552), ('indexation', 0.00942288891103746), ('seul grand jeu', 0.00815934704646957), ('élaboration automatique', 0.007934840632379673), ('partie', 0.007852323971092444), ('bibliothèques numériques scientifiques', 0.007781006739930199), ('hypothèses', 0.007773714027071121), ('bout-en-bout', 0.007762056434164916), ('état', 0.007272635379522483)],
2:[('mots-clés', 0.06067720763173498), ('documents scientifiques', 0.04301424489079034), ('méthodes', 0.02204135670211993), ('indexation', 0.014996041642937009), ('mot', 0.013825592294186952), ('annotateur', 0.010805042563395265), ('candidats', 0.009877209879481237), ('nombre', 0.009532286726006593), ('concepts', 0.009403004240326055), ('indexeurs professionnels', 0.008451351828558608), ('extraction', 0.008402269122037509), ('graphes', 0.008253902722630328), ('auteurs', 0.008072424742431035), ('données terminologiques', 0.007282568955553803), ('noms', 0.007122538943832972), ('termes', 0.007005254636497093), ('exemple', 0.006892051775787601), ('patrons morphosyntaxiques', 0.006715096964964548), ('mots-clés candidats', 0.006617907493050932), ('france', 0.006509315409700584)],
3:[('mots-clés', 0.04400309622838112), ('mots', 0.028616126286458647), ('documents', 0.02654124080823226), ('méthodes', 0.025393331029240972), ('génération', 0.019005929368766123), ('séquences', 0.018268208715675038), ('réseaux', 0.013905772621936263), ('mécanisme', 0.013771040082561362), ('modèle', 0.011908945379818462), ('neurones', 0.01066138023126358), ('état', 0.009020232892309285), ('fonction', 0.00888462063897445), ('vocabulaire', 0.00865971415236842), ('représentation', 0.008426139482412132), ('attention', 0.008226444780870151), ('section', 0.008009196660165372), ('entrée', 0.007895054558875477), ('sortie', 0.007548269954593166), ('décodage', 0.007394934633838165), ('encodeurs', 0.007047379544979781)],
4:[('mots-clés', 0.042269632049400124), ('données', 0.03570968910000773), ('documents scientifiques', 0.034593244135375505), ('différents jeux', 0.02668079258832608), ('articles', 0.015530644378103009), ('méthodes', 0.012191225041549378), ('annotation', 0.012067041903483561), ('jeu', 0.009837821511815321), ('langue anglaise', 0.009440590695620126), ('références bibliographiques', 0.009218509750185438), ('chapitre 4cadre expérimental', 0.008825642260521863), ('évaluation', 0.00873209750680325), ('production automatique', 0.008726147828069984), ('moyenne', 0.008626604784337254), ('notices scientifiques', 0.008548898797047734), ('ensembles', 0.00842386292088164), ('auteurs', 0.007332717321228995), ('données journalistiques', 0.007018178275046003), ('domaine général', 0.0069712351963694035), ('nombre', 0.006862248197164503)],
5:[('mots-clés', 0.04535610529242023), ('documents', 0.03375470601014565), ('articles journalistiques', 0.027628509912325988), ('données', 0.020725960429722367), ('méthodes neuronales génératives', 0.018875957371819765), ('annotateurs', 0.016030801872114066), ('kp20k', 0.014579135318315936), ('mots-clés éditeurs', 0.01354390509905409), ('ensemble', 0.012160731800369359), ('jeu', 0.01126192295915727), ('performances', 0.011056570291348367), ('principaux jeux', 0.010375789216738289), ('modèle', 0.009879947820410987), ('copynews', 0.009475899003675684), ('test', 0.008976556807273781), ('différents domaines', 0.008560001248617945), ('généralisation', 0.008181058789408275), ('production', 0.008167599731266758), ('york times', 0.007224428766555271), ('cohérence', 0.006742961176522095)],
6:[('méthodes', 0.054005592310461446), ('données', 0.032019551932407124), ('documents', 0.02306930667901198), ('mots-clés', 0.02299724505165436), ('performances', 0.018588384444009367), ('autres jeux', 0.018481269366018304), ('évaluation', 0.014866647046622461), ('modèles', 0.013681649538503099), ('entraînement', 0.013107897668081193), ('base', 0.01223734045238173), ('ensembles', 0.01047790636216139), ('articles', 0.009715603701482807), ('annotation', 0.009671728099160459), ('seul mot', 0.008624111846537613), ('production automatique', 0.0084063869240403), ('chapitre 6évaluation', 0.008374323306476259), ('référence', 0.007177531421505665), ('candidats', 0.006469661216164908), ('différences', 0.0064566392113257105), ('copyrnn', 0.006433788015864928)],
7:[('mots-clés', 0.06183643289268983), ('documents', 0.03806127907030812), ('requête', 0.0206627369237207), ('recherche', 0.018679104498319953), ('pertinente', 0.01713914058002797), ('mots', 0.016150197459654965), ('score', 0.01276744486626708), ('information', 0.012636341959489362), ('indexation', 0.011873845429819065), ('référence', 0.011439007275151914), ('méthodes', 0.011225660049353707), ('chapitre 7impact', 0.010581375737222481), ('systèmes', 0.010469816738441598), ('résultats', 0.009532892544436204), ('mots-clés présents', 0.009116980245315213), ('ajout', 0.008192956153757532), ('corrrnn', 0.00789792933768759), ('impact', 0.007185114665108302), ('mots-clés absents', 0.007076623035944837), ('nombreux domaines', 0.007043183422343777)],
9:[('mots-clés', 0.06395145201941259), ('méthodes actuelles', 0.03856182720481847), ('évaluation', 0.024617505870606425), ('document', 0.023322044433239816), ('production automatique', 0.022084894404785588), ('annotation', 0.01742440186150521), ('recherche', 0.016383645836271752), ('référence', 0.015020568651581103), ('données', 0.014342482728979844), ('tâche', 0.01416415217323381), ('bons résultats', 0.012294892827562139), ('grand jeu', 0.010025664811000952), ('évaluation extrinsèque', 0.009587106565968471), ('importants', 0.009514748262702795), ('information', 0.00925369216769912), ('processus', 0.008323453265780757), ('entraînement', 0.008264510869691107), ('modèles neuronaux', 0.008202053771627735), ('méthodes génératives', 0.008090414638019313), ('contributions principales', 0.008035358892728058)],
'all':['mots-clés', 'documents scientifiques', 'premières méthodes', 'données différentes', 'mots importants', 'chapitre 1introduction', 'production automatique', 'jeux', 'performances', 'référence', 'recherche documentaire', 'articles', 'annotation', 'ensemble', 'évaluation pessimiste', 'nombre', 'modèles', 'mots-clés absents', 'indexation', 'seul grand jeu']
]


data = [{
	'id': c[0].split(' ')[0] if c[0][0].isdigit() else c[0][9],
	'title': c[0],
	'abstract': ''.join(c[1:])}
	for c in acc if c]

with open('data_section.jsonl', 'w') as f:
	for d in data:
		f.write(json.dumps(d) + '\n')