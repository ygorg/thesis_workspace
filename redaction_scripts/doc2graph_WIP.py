
# afficher un document sous forme de graphe
import pke
import random
from glob import glob
import networkx as nx
import matplotlib.pyplot as plt
plt.switch_backend('webagg')
files = glob('ake-datasets/datasets/TALN-Archives-fr/test/*.xml')
files += glob('TALN-Archives-fr/test/*.xml')

def aa(f):
    e = pke.unsupervised.PositionRank()
    e.load_document(f, language='fr')
    e.candidate_selection()
    e.candidate_weighting()
    return e.graph, e

g, e = aa(random.choice(files))
pos = nx.spring_layout(g)
nx.draw(g, pos, with_labels=True)
nx.draw_networkx_edge_labels(g, pos, edge_labels={e: str(e) for e in g.edges})
plt.show()


import matplotlib as mpl
mpl.use('webagg')
import matplotlib.pyplot as plt
plt.plot([1], [1])
plt.show()