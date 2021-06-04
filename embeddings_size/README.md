# Embedding dimension

EN FAIT LES EMBEDDING DE SORTIE DEPUIS LE DEBUT ONT UNE TAILLE DE 30 OMG

Calculer les scores avec la prédiction

1. Est-ce que mettre une taille de 150 (comme l'entrée) change de manière significative les résultats ?
	Pour les présent ?
	Pour les absent ? (vraiment ce serait une blague)

2. Plus pour le fond. Est-ce que partager les embeddings améliore les résultats ?


| P    | R    | F    | MAP  | n  | model  |
| ----:| ----:| ----:| ----:| --:|:------------- |
| 28.0 | 29.5 | 27.5 | 28.1 |  5 | bigembed KP20k.test.stem.json |
| 27.4 | 28.7 | 26.8 | 27.4 |  5 | shared KP20k.test.stem.json |
| 28.2 | 29.6 | 27.6 | 28.5 |  5 | copyless KP20k.test.stem.json |
| 19.6 | 40.0 | 25.1 | 28.1 | 10 | bigemebd KP20k.test.stem.json |
| 19.3 | 39.3 | 24.6 | 27.4 | 10 | shared KP20k.test.stem.json |
| 19.8 | 40.2 | 25.2 | 28.5 | 10 | copyless KP20k.test.stem.json |
