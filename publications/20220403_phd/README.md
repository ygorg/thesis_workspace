Pour compiler:

```bash
pip install pygments
pygmentize -V  # should display version number
pdflatex --shell-escape main.tex 
bibtex main.tex
pdflatex --shell-escape main.tex 
pdflatex --shell-escape main.tex 
```

Pour imprimer une version en couleur : ne pas afficher les liens en bleu dans `hypersetup`, ainsi il y a moins de pages à imprimer en couleurs et c'est moins cher !
Pour une version numérique : supprimer l'option `twoside` dans `\documentclass[twoside,12pt,a4paper]{report}` ainsi il n'y a pas de différence entre les pages paires et immpaires.
