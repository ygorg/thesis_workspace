# Exploration ISTEX

## Etude de faisabilité
1. Sur 30000 documents 8055 possèdent des sujets (mots-clés) et un résumé
2. Identifier la langue du titre et résumé pour filtrer les document d'une autre langue
3. Filtrer les mots-clés non français

https://dl.istex.fr/document/?q=(language:fre+AND+pratique+textile)&extract=metadata[json]&size=30000&rankBy=random&archiveType=tar&compressionLevel=9&sid=istex-dl&usage=1&total=84080


```bash
mkdir "istex-test"
cd "istex-test"
mv "../istex-subset-2021-10-25.tar.gz" .
tar -xvf "istex-subset-2021-10-25.tar.gz"
```

```python
import json
from glob import glob

files = glob('*/*.json')

to_extract = ['doi', 'arkIstex', 'title', 'abstract', 'subject', 'publicationDate'] # 'categories'

data = []

for fp in files:
    with open(fp) as f:
        metadata = json.load(f)
    if not all(k in metadata for k in ['subject', 'abstract', 'title']):
    	continue
    metadata['subject'] = [e['value'] for e in metadata['subject'] if 'value' in e]
    data.append({k: metadata[k] for k in to_extract if k in metadata})
```

```python
# Exemple de document extraits: les mots-clés sont en anglais et français parfois
# Le titre est français, le résumé en anglais
# Les sujets sont séparés par des '-'
[
    {'doi': ['10.1016/0147-9571(80)90037-5'],
    'arkIstex': 'ark:/67375/6H6-RHG8HRQX-F',
    'title': "Surveillance epidemiologique des grippes humaines dans le monde: Le programme de l'OMS",
    'abstract': "Résumé: La surveillance internationale de la grippe est une des premières missions de l'OMS. Elle est basée sur les rapports épidémiologiques des Etats Membres et les activités d'un réseau de 101 laboratoires de virologie dans 72 pays. Ces laboratoires reçoivent les réactifs nécessaires pour l'identification des souches. Toute souche présentant des caractères antigéniques inhabituels est envoyée sans délai aux deux centres mondiaux de Londres et d'Atlanta (U.S.A.) pour caractérisation complète et éventuellement pour sa distribution aux fabricants de vaccin. La reconnaissance des ‘glissements’ ou des ‘cassures’ antigéniques et de leur signification épidémiologique est parfois difficile et nécessite la réunion d'un groupe d'experts. La rapidité de ces actions est une règle impérative.",
    'subject': ['Maladies à virus',
    'grippe humaine',
    'surveillance épidémiologique',
    'programmes OMS',
    'sélection souches vaccinales de la grippe',
    'Viral diseases',
    'human influenza',
    'epidemiological surveillance',
    'WHO programmes',
    'selection of vaccine strains against influenza'],
    'publicationDate': '1980'},
    {'doi': ['10.1007/s00038-003-1116-9'],
    'arkIstex': 'ark:/67375/VQC-7N136KT7-3',
    'title': "Santé psychologique des étudiants et identification des personnes à risque: le retrait d'examen comme symptôme de la dépression",
    'abstract': 'Summary: Student psychological health and the problem of identifying at-risk individuals: withdrawing from an exam session as a symptom of depressionObjective: Our exploratory study concerning student psychological health was aimed at identifying possible subgroups of at-risk students within a college-student population.Method: A total of 445 students answered four questionnaires (three standard psychometric instruments and an ad hoc questionnaire comprising 50 multiple-choice questions). We then searched for risk-groups by studying all answers obtained with the ad hoc questionnaire and looking for those answers that were significantly correlated with ratings of psychopathology. To carry out this search, we used first and second order principal components factor analysis.Results: Our results show that the incidence of depression is almost twice as high among students that have withdrawn from an exam session than among the other students in our sample. It is further possible to determine that, in our sample, it is not withdrawing from an exam session that causes depression but, rather, it is depression that increases the probability of withdrawing from an exam session.Conclusion: It thus definitely seems that, unlike flunking exams, withdrawing from exams is often a symptom of depression.',
    'subject': ['Mental health', 'Risk factors', 'Switzerland', 'Depression.'],
    'publicationDate': '2003'},
    {'doi': ['10.1016/S0222-9617(01)80078-7'],
    'arkIstex': 'ark:/67375/6H6-6QSVBGJ4-C',
    'title': "L'enfant face à la maladie mentale de ses parents. Impact et traitement en placement familial",
    'abstract': "Résumé: Les troubles de la fonction parentale (ou dysparentalité) des parents malades mentaux font courir à leur enfant des risques psychiques et parfois vitaux. Une séparation avec accueil en placement familial thérapeutique peut alors être prescrite, le plus souvent par décision judiciaire, pour permettre un soin pour l'enfant et pour la relation parent-enfant. Dans ce travail basé sur une pratique en placement familial thérapeutique sont analysés les processus psychopathologiques infiltrant la fonction parentale, leur impact sur le développement psychique de l'enfant et le travail autour de la relation objectale par le biais des rencontres médiatisées parents-enfant s'appuyant sur une pratique spécifique, l'accompagnement thérapeutique.",
    'subject': ['disparentality / mediated visits / mentally ill parents / therapeutic accompaniment / therapeutic foster-family',
    'accompagnement thérapeutique / dysparentalité / médiatisation / parents malades mentaux / placement familial thérapeutique / rencontres parent-enfant'],
    'publicationDate': '2001'}
]

```

