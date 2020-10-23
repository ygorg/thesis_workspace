# OpenNMT


## Pre-traitement

### Créer les fichiers *src* et *tgt*

OpenNMT prend en entrée un fichier source avec un document par ligne et un fichier target avec une target par ligne. Les documents doivent être prétraités, aucun traitement ne sera fait après.
`opennmt_preprocess` calcule les vocabulaires et transforme ces fichiers en tenseurs.


#### Calculer le vocabulaire (optionnel)

Pour le KPE chaque document crée N exemples (N est le nombre de TC du doc). Comme on duplique les articles, on augmente la fréquence de leur mots par rapport au mots des termes-clés (Les mots des TC auront moins de chance de se trouver dans le voc final).


```python
import os
import re
import json
from tqdm import tqdm
from collections import Counter
import nltk
from multiprocessing import Pool
from more_itertools import grouper

# Stolen from https://github.com/kenchan0226/keyphrase-generation-rl/blob/1a3b20be236732fa20137690ce463cabc4b527e3/integrated_data_preprocess.py#L307

digit = re.compile(r'^[+-]?((\d+(\.\d*)?)|(\.\d+))$')

def replace_digit(tokens):
    return ['<digit>' if digit.match(t) else t
            for t in tokens]


def doc2voc(line):
    # Create a list of tokens to be counted for the vocabulary.
    doc = json.loads(line)

    # Document loading
    src = doc['title'] + ' . ' + doc['abstract']
    src_tokens = nltk.word_tokenize(src)
    # Chargement des termes-clés
    tgt_lst = doc['keyword']
    if type(['keyword']) is str:
        tgt_lst = tgt_lst.split(';')
    tgt_tokens = map(nltk.word_tokenize, tgt_lst)

    # Prétraitement des mots pour le vocabulaire
    src = src_tokens + sum(tgt_tokens, [])
    src = replace_digit(src)
    return src


def batch_doc2voc(b):
    return [doc2voc(d) for d in b if d]


def compute_voc(input_file, output_file, voc_size, n_thread=None):
    voc = Counter()
    with open(input_file) as f:
        f = tqdm(f)
        if not n_thread or n_thread < 2:
            data = map(doc2voc, f)
            for doc in data:
                voc.update(doc)
        else:
            with Pool(n_thread) as p:
                batch = grouper(f, 50)
                batch = p.imap_unordered(batch_doc2voc, batch)
                data = chain.from_iterable(batch)
                for doc in data:
                    voc.update(doc)
    with open(output_file, 'w') as f:
        for t, _ in voc.most_common(voc_size):
            f.write(f'{t}\n')

voc_size = 50000
dataset = 'RefSeerX'
split = 'train'

in_path = f'data/datasets/{dataset}'
out_dir = in_path

input_file = os.path.join(in_path, f'{dataset}.{split}.jsonl')
output_file = os.path.join(out_dir, f'{dataset}.{split}.voc')

compute_voc(input_file, output_file, voc_size)
```


#### Creer les fichiers alignés source

```python
import os
import re
from itertools import chain
import nltk
import json
from tqdm import tqdm
from multiprocessing import Pool
from more_itertools import grouper

# Stolen from https://github.com/kenchan0226/keyphrase-generation-rl/blob/1a3b20be236732fa20137690ce463cabc4b527e3/integrated_data_preprocess.py#L307

digit = re.compile(r'^[+-]?((\d+(\.\d*)?)|(\.\d+))$')

def replace_digit(tokens):
    return ['<digit>' if digit.match(t) else t
            for t in tokens]

def doc2src_tgt_o2o(line):
    # Pour chaque document on crée autant d'instance que de TC
    doc = json.loads(line)

    # Chargement du document
    src = ' . '.join([doc['title'], doc['abstract']])
    src = nltk.word_tokenize(src)
    tgt_lst = doc['keyword']
    if type(tgt_lst) is str:
        tgt_lst = tgt_lst.split(';')
    tgt_lst = map(nltk.word_tokenize, tgt_lst)

    # Prétraitement de la source et des TC
    src = ' '.join(replace_digit(src))
    tgt_lst = map(replace_digit, tgt_lst)
    tgt_lst = map(' '.join, tgt_lst)
    for tgt in tgt_lst:
        yield src, tgt

def batch_doc2src_tgt_o2o(batch):
    return [res for line in batch if line
            for res in doc2src_tgt_o2o(line)]

def compute_src_trg(input_file, output_file, n_thread=None):
    with open(input_file) as f:
        src_file = open(output_file + '.src', 'w')
        tgt_file = open(output_file + '.tgt', 'w')
        f = tqdm(f)
        if not n_thread or n_thread < 2:
            data = map(doc2src_tgt_o2o, f)
            data = chain.from_iterable(data)
            for src, tgt in data:
                src_file.write(src + '\n')
                tgt_file.write(tgt + '\n')
        else:
            with Pool(n_thread) as p:
                batch = grouper(f, 50)
                batch = p.imap(batch_doc2src_tgt_o2o, batch)
                data = chain.from_iterable(batch)
                for src, tgt in data:
                    src_file.write(src + '\n')
                    tgt_file.write(tgt + '\n')
        src_file.close()
        tgt_file.close()


dataset = 'RefSeerX'
in_path = f'data/datasets/{dataset}'
out_path = in_path

for split in ('test', ):
    input_file = os.path.join(in_path, f'{dataset}.{split}.jsonl')
    output_file = os.path.join(out_path, f'{dataset}.{split}')
    n_thread = 0
    if split == 'train':
        n_thread = 4
    compute_src_trg(input_file, output_file, n_thread=n_thread)
```


### Preprocess

Indexe les exemples d'entrainement/validation avec le vocabulaire.


```bash
DATASET="RefSeerX"
DATA_DIR="../data/datasets/${DATASET}/min"
DATA_PREFIX="data/${DATASET}/min"
# --dynamic_dict in order to use copy
onmt_preprocess \
    --train_src $DATA_DIR/${DATASET}.train.src --train_tgt $DATA_DIR/${DATASET}.train.tgt \
    --valid_src $DATA_DIR/${DATASET}.valid.src --valid_tgt $DATA_DIR/${DATASET}.valid.tgt \
    --src_vocab $DATA_DIR/../${DATASET}.train.voc --tgt_vocab $DATA_DIR/../${DATASET}.train.voc \
    --share_vocab --dynamic_dict --src_seq_length 400 --tgt_seq_length 10 --filter_valid \
    --save_data $DATA_PREFIX  --shard_size 100000 --num_threads 5 --report_every 5000
```

## Entraînement

```bash
DATA_PREFIX="data/${DATASET}/min"

EXPNAME="copyRNN_${DATASET}"
ROOT="experiments/$EXPNAME"
mkdir -p $ROOT
# Pour entrainer 10 epochs il faut connaitre la taille du corpus de train
#  et passer à train_steps `len(train) / batch_size * 10`
onmt_train \
    --word_vec_size 150 --encoder_type brnn --decoder_type rnn --layers 2 --rnn_size 300 --rnn_type GRU \
    --global_attention mlp --copy_attn \
    --early_stopping 4 --optim adam --max_grad_norm 0.1 --dropout 0.5 --learning_rate 0.0001 \
    --batch_size 128 --save_checkpoint_steps 20000 --valid_steps 20000 --train_steps 200000 --report_every 500 \
    --data $DATA_PREFIX --save_model $ROOT/model --exp $EXPNAME --gpu_ranks 0 \
    --tensorboard_log_dir $ROOT/log --log_file $ROOT/$EXPNAME.log --tensorboard
```

Meng's model:
- How many layers ? how to pass from enc to dec ? is 300 the size of for+back or for is 300 and back is 300
- no info about nb of layers, thought the dropout in onmt implies layers > 1 so using 2 layers ?

Onmt:
-si 'brnn' alors 'hidden_size' est le total de poids pour -> et <- (https://github.com/OpenNMT/OpenNMT-py/blob/fae4d620ff94113e9c0cb2cd4e71e46635b79aa9/onmt/encoders/rnn_encoder.py#L33)
-si copy_attn alors il faut passer dynamic-vocabulary au preprocessing


## Evaluation

Lancer la commande `onmt_translate` qui écrit les TC de sortie dans le même format que les fichiers target.

```bash
# n_best dit combien de sequence sont écrite dans l'output
BEAMSIZE=50
INPUT_=../data/datasets/KP20k.test.txt
MODEL=model_step_300000
OUTPUTNAME=$(echo $INPUT_ | sed 's!.*/\(.*\).txt!\1!g')
onmt_translate \
    --model $ROOT/$MODEL.pt --src $INPUT_ \
    --output $ROOT/predictions/$OUTPUTNAME.$EXPNAME.$BEAMSIZE.$MODEL.txt \
    --beam $BEAMSIZE --max_length 6 --n_best $BEAMSIZE --batch_size 18 --gpu 0
```


Ce script permet de transformer le fichier de sortie de `onmt_translate` en fichier `json`.
Il filtre les TC qui contiennent des tokens spéciaux (digit, unknown) et execute la racinisation.

```python
import re
import nltk
import json
from tqdm import tqdm
import argparse
import os

stem = nltk.stem.PorterStemmer().stem


def clean_output(lines):
    lines = (l.lower().strip() for l in lines)
    lines = [l for l in lines if not re.search(r'<\w+>', l)]
    stemmed = [' '.join(stem(w) for w in l.split(' ')) for l in lines]
    lines = [([k], [s]) for i, (k, s) in enumerate(zip(lines, stemmed))
             if s not in stemmed[:i]]
    return [k for k, s in lines], [s for k, s in lines]

if __name__ == '__main__':
    def arguments():
        parser = argparse.ArgumentParser()
        parser.add_argument('file', type=argparse.FileType('r'), help='Prediction file in jsonl format')
        parser.add_argument('--no-stem', action='store_true',
                            help='Output non stemmed keyphrases')
        return parser.parse_args()

    args = arguments()

    here_path = os.path.dirname(__file__) or '.'
    input_file = args.file.name
    output_file = input_file.replace('.txt', '.json' if args.no_stem else '.stem.json')
    if os.path.isfile(output_file):
        resp = input(f'Output file already exist. Enter [Y/y] to overwrite ({output_file})\n')
        if resp.lower() != 'y':
            print('Exitng...')
            exit()

    corpus, split, _ = os.path.basename(input_file).split('.', maxsplit=2)

    res = {}
    with open(f'{here_path}/../data/datasets/{corpus}.{split}.jsonl') as f:
        with open(input_file) as g:
            for doc in map(json.loads, tqdm(f)):
                lines = [g.readline() for _ in range(50)]
                kps, kps_s = clean_output(lines)
                res[doc['id']] = kps if args.no_stem else kps_s

    with open(output_file, 'w') as f:
        json.dump(res, f)
```
