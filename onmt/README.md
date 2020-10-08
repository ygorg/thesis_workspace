# OpenNMT


## Pre-traitement

### Créer les fichiers *src* et *tgt*

OpenNMT prend en entrée un fichier source avec un document par ligne et un fichier target avec une target par ligne. Les documents doivent être prétraités, aucun traitement ne sera fait après.
`opennmt_preprocess` calcule les vocabulaires et transforme ces fichiers en tenseurs.


#### Calculer le vocabulaire (optionnel)

Pour le KPE chaque document crée N exemples (N est le nombre de TC du doc). Comme on duplique les articles, on augmente la fréquence de leur mots par rapport au mots des termes-clés (Les mots des TC auront moins de chance de se trouver dans le voc final).


```python
import re
import json
from tqdm import tqdm
from collections import Counter


def replace_digit(string):
    string = re.sub(r'(\d*[.,])?\d+', ' <digit> ', string)
    string = re.sub(r' +', ' ', string).strip()
    return string


def doc2voc(line):
    doc = json.loads(line)

    # Chargement du document
    src = ' '.join([doc['title'], doc['abstract']])
    src = ' '.join(nltk.word_tokenize(src))
    tgt_lst = doc['keyword'].split(';')

    # Prétraitement des mots pour le vocabulaire
    src = ' '.join((src, ' '.join(tgt_lst)))
    src = replace_digit(src)
    return src.split(' ')


dir_path = 'data/datasets/KP20k/full'
split = 'train'
voc = Counter()
with open(f'{dir_path}/kp20k.{split}.json') as f:
    data = map(doc2voc, tqdm(f))
    for doc in data:
        voc.update(doc)
sorted(w for w, n in voc.most_common(50000))
```


#### Creer les fichiers alignés source

```python
from itertools import chain


def doc2src_tgt_o2o(line):
    # Pour chaque document on crée autant d'instance que de TC
    doc = json.loads(line)

    # Chargement du document
    src = ' '.join([doc['title'], doc['abstract']])
    src = ' '.join(nltk.word_tokenize(src))
    tgt_lst = doc['keyword'].split(';')

    # Prétraitement de la source et des TC
    src = replace_digit(src)
    tgt_lst = [replace_digit(k) for k in tgt_lst]
    for tgt in tgt_lst:
        yield src, tgt


def file2instance(file):
    return chain.from_iterable(map(doc2src_tgt_o2o, f))


dir_path = 'data/datasets/KP20k/full'
split = 'valid'
with open(f'{dir_path}/kp20k.{split}.json') as f:
    src_file = open(f'src.{split}', 'w')
    tgt_file = open(f'tgt.{split}', 'w')
    for src, tgt in file2instance(tqdm(f)):
            src_file.write(src + '\n')
            tgt_file.write(tgt + '\n')
    src_file.close()
    tgt_file.close()
```


### Preprocess

Indexe les exempels d'entrainement/validation avec le vocabulaire.


```bash
DATA_DIR="../data/datasets/KP20k/full_less_corenlp"
DATA_PREFIX="data/kp20k_full_less_corenlp"
# --dynamic_dict in order to use copy
onmt_preprocess \
    --train_src $DATA_DIR/src.train --train_tgt $DATA_DIR/tgt.train \
    --valid_src $DATA_DIR/src.valid --valid_tgt $DATA_DIR/tgt.valid \
    --src_vocab $DATA_DIR/src_tgt.voc --tgt_vocab $DATA_DIR/src_tgt.voc \
    --share_vocab --dynamic_dict --src_seq_length 400 --tgt_seq_length 10 --filter_valid \
    --save_data $DATA_PREFIX  --shard_size 100000 --num_threads 5 --report_every 5000
```

## Entraînement

```bash
DATA_PREFIX="data/kp20k_full_less_corenlp"

EXPNAME="copyRNN"
ROOT="experiments/$EXPNAME"
mkdir -p $ROOT
# Pour entrainer 10 epochs il faut connaitre la taille du corpus de train
#  et passer à train_steps `len(train) / batch_size * 10`
onmt_train \
    --word_vec_size 150 --encoder_type brnn --decoder_type rnn --layers 1 --rnn_size 300 --rnn_type GRU \
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
