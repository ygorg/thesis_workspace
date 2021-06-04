# Expé evaluation modèles par la RI

Les scores des modèles présentés augmentent et sont entre 30 et 40% de F@5.
Cette augmentation dans les performances de production de mots-clés se reporte-t-elle sur les scores de RI ?
Si oui pk ?
- meilleure qualitée des mc
Si non pk ?
- les mc générés sont présent, ce sont les abs qui sont utile pour la ri
- les mc ne sont pas assez qualitatifs


1ere étape : obtenir les sortie des modèles
[x] lister les papiers avec du code disponible

KP20k
| papier      | Arx | F@5 P | F@10 P | lien |
| chen 2018   |     |       | 21.8   |  |
|bahuleyan 2020|    | 26.9  |        |  | @M ALL
| chen 2020   |     | 31.1  |        | https://github.com/Chen-Wang-CUHK/ExHiRD-DKG |
| chen 2019   |     | 31.7  | 28.2   |  | ALL
| chan 2019   |     | 32.1  |        |  |
| meng 2017   |     | 33.3  | 26.2   |  |
| yuan 2020   |     | 34.8  | 29.8   |  |
| ye 2021     |  ?  | 35.8  |        |  |
| diao 2020   |  X  | 38.1  | 32.4   | https://github.com/SVAIGBA/CDKGen |

| martinc 2020|  X  | 28.38 | 28.7   | X |
| sun 2020    |  X  | 41.9  | 34.4   | https://github.com/thunlp/BERT-KPE |


[] choisir les méthodes a executer
	- essayer d'avoir des papiers dont les perf reportées sont différentes et augmentent
[] essayer d'executer le code