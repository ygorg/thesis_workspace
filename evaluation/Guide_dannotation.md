# Guide d'annotation

Le but est d’annoter des termes-clés prédits associés à un document comme positif ou négatif en fonction d’un ensemble de termes-clés de référence.
Les termes-clés prédit égaux à la référence ne sont pas affichés.

Mots en plus : plus précis

| Reference       |   | Candidat                    | Description |
| --------------- | - | --------------------------- | ----------- |
| sentient object | 🟢 | sentient object model       | décrit un concept |
| sentient object | 🔴 | sentient object programming | décrit un type de programmation |

Mots en moins : moins précis mais pas trop vague

| Reference              |   | Candidat        | Description |
| ---------------------- | - | --------------- | ----------- |
| cell therapy           | 🔴 | cell            | Trop vague |
| automatic classifiers  | 🟢 | classification  | On fait de la "classification" avec des "automatic classifier" on référe au même concept |
| automatic moderation   | 🟢 | moderation      | C'est toujours de la modération |
| support vector machine | 🔴 | support vector  | "support vector" ne veut pas dire "SVM" |

Synonyme / Hypernymes :

Dans ces cas-là, si la décision prend plus de 10s annoter comme négatif. Si il est clair que les termes-clés sont lié alors annoter comme positif.

| Reference                    |   | Candidat               | Description |
| ---------------------------- | - | ---------------------- | ----------- |
| left ventricular contraction | 🟢 | cardiac contraction    | "left ventricular" est une partie du coeur "cardiac" |
| ad hoc wireless networks     | 🔴 | mobile ad hoc networks | N'étant pas un expert du domaine "mobile" et "wireless" parraissent liés |
| gender identification        | 🔴 | authorship attribution | Dans le contexte le "gender identification" sert pour l'"authorship attribution" |




## Version Alpha
Le but est d’annoter des termes-clés prédits associés à un document comme positif ou négatif en fonction d’un ensemble de termes-clés de référence.
Les termes-clés prédit égaux à la référence ne sont pas affichés.
Chaque terme-clé prédit doit avoir 1 étiquette au maximum.
Il est possible d’annoter “Bon” ou “Mauvais”.
Pour une analyse plus fine il est possible d’associer une lettre correspondant au critère de choix de l’annotation (voir ci-dessous).
Les critères de choix de l’étiquette “Bon” et “Mauvais” sont décrits ci-dessous.
Bons:
- (P) Perfect match, mêmes mots
- (M+nb) Match, mots différents mais même sens
	- ex: “decision tree” et “decision tree model”
- (O+nb) Surspécification d’un TC de référence.
	- ex:  “pronunciation model” et “stochastic pronunciation model”
	- Ici “stochastic” rend “pronunciation model” plus spécifique.
- (G) général et qui englobe le document (tâche, domaine, ...)
- (I) ne fait pas partie de la référence mais est intéréssant dans le contexte pour l’indexation
Mauvais:
- (m) n’est pas un concept majeur dans le contexte.
	- ex: “multiword approach” dans le contexte n’est pas un concept clé du document (l’article utilise une approche multimot mais ce n’est pas le coeur de l’article)
- (p) trop précis
- (v) trop vague
- (X) n’a pas de rapport, pas syntaxiquement correct, contient des stop words