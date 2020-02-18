# Calcul d'Oracle

## Idées
- Utiliser un très gros beam et calculer PRF@200, ou un rappel max (Meng l'a fait pour les absent seulement)
- Calculer la probabilité des références (comme à l'entrainement) pour attester de la modélisation des termes-clés par le modèle. Ou alors pour chaque token quel est son rang et donc quel serais le beam à utiliser pour avoir un TC (ce serais le rang max)