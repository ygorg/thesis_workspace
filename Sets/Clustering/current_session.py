# coding: utf-8
from allennlp.data.vocabulary import Vocabulary
import torch
model = torch.load('model_state_epoch_4.th')
model['_target_embedder.weight'].shape
v = Vocabulary.from_files('vocabulary')
v
v.keys
v.get_token_to_index_vocabulary('tokens')
dd = v.get_token_to_index_vocabulary('tokens')
{k: v for k, v in dd.items() if k.startswith('event')}
dd = v.get_token_index()
dd = v.get_token_index('tokens')
dd
def i2t(i):
    return v.get_token_from_index(i)
    
def t2i(t):
    return v.get_token_index(t)
    
embeddings = model['_target_embedder.weight']
del model
def embed(i):
    if isinstance(i) is str:
        i = t2i(i)
    return embeddings[i]
    
embed(8)
def embed(i):
    if isinstance(i, str):
        i = t2i(i)
    return embeddings[i]
    
embed(8)
embed('event')
t2i('event')
embeddings[993]
torch.cosine_similarity(embed('event'), embeddings)
torch.cosine_similarity(embed('event'), embeddings, 0)
torch.cosine_similarity(embed('event'), embeddings, 1)
torch.cosine_similarity(embed('event'), embeddings, -1)
torch.cosine_similarity(embed('event'), embeddings, -1).shape
torch.cosine_similarity(embed('event'), embeddings, -1).topk(10)
p, i = torch.cosine_similarity(embed('event'), embeddings, -1).topk(10)
list(map(i2t, i))
[i2t(e.item()) for e in e] 
[i2t(e.item()) for e in i] 
p
p, i = torch.cosine_similarity(embed('event'), embed('event.'), -1).topk(10)
p, i = torch.cosine_similarity(embed('event'), embed('event.'), -1)
p, i = torch.cosine_similarity(embed('event'), embed('event.'))
p, i = torch.cosine_similarity(embed('event'), embed('event.'), 0)
p, i = torch.cosine_similarity(embed('event'), embed('event.').view(1, -1), 0)
torch.cosine_similarity(embed('event'), embed('event.').view(1, -1), 0)
torch.cosine_similarity(embed('event'), embed('event.').view(1, -1), 1)
torch.cosine_similarity(embed('event'), embed('event.').view(1, -1), -1)
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import offsetbox
from sklearn import (manifold, datasets, decomposition, ensemble,
                     discriminant_analysis, random_projection, neighbors)
get_ipython().run_line_magic('save', 'current_session ~0/')
