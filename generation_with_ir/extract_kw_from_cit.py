import json
import nltk
from tqdm import tqdm
from multiprocessing import Pool
from more_itertools import grouper
from nltk import RegexpParser
from collections import Counter
import spacy
import re

def grammar_selection(doc, chunker):
    # initialize chunker
    tuples = [(e.text, e.pos_) for e in doc]
    tree = chunker.parse(tuples)
    acc = []
    # find candidates
    for subtree in tree.subtrees():
        if subtree.label() == 'NP':
            acc.append(' '.join(l[0] for l in subtree.leaves()))
    return acc


def get_sent(d):
    return [s for s in nltk.sent_tokenize(d) if '=-=' in s]


def pretreat_ctxt(ctxt):
    doc = get_sent(ctxt[1])
    if not doc:
        return None
    doc = doc[0]
    doc = doc.replace('-=-', '').replace('=-=', '')
    doc = doc.replace('[', ' [').replace(']', '] ')
    return doc


# Composed only of 1 or 2 characters words
word_len = lambda k: not all(len(t) < 2 for t in k.split(' '))
# Has more that 70% of punctuation
letter_ratio = lambda k: len(k) <= 4 or \
    (sum(c.isalnum() or c == ' ' for c in k) / len(k) > 0.7)
# Has special characters (math symbols, russian script, ...)
spe_char = lambda k: all(ord(' ') <= ord(c) <= ord('z') for c in k)
# Contains more than 6 words
len_kw = lambda k: len(k.split(' ')) < 7
# Comprises a citation
et_al = lambda k: not re.findall(r'\bet al\b', k)
all_filt = [spe_char, word_len, letter_ratio, len_kw, et_al]


def process_one(line, nlp, chunker):
    d = json.loads(line)
    if 'keyword' in d:
        d['author_keyword'] = d['keyword']
    if not letter_ratio(d['title'] + ' ' + d['abstract']):
        # Document have more than 70% of punctutaion
        continue
    ctxt = map(pretreat_ctxt, d['ctxt'])
    ctxt = filter(None, ctxt)
    ctxt = nlp.pipe(ctxt, batch_size=50)
    kws = map(lambda x: grammar_selection(x, chunker), ctxt)
    break  # count in how many ctxt a kws appear !!!!!!! (so compute df instead of frequency)
    kws = Counter(k for c in kws for k in c)

    kws = (k for k, v in kws.items() if v > 1)
    # Filter out noisy keywords
    for filt in all_filt:
        kws = filter(filt, kws)
    d['keyword'] = ';'.join(kws)

    if not d['keyword']:
        return None
    del d['ctxt']
    return json.dumps(d) + '\n'


def process_many(lines):
    global nlp, chunker
    return [process_one(l, nlp, chunker) for l in lines if l]


def init_worker():
    global nlp, chunker
    nlp = spacy.load('en', disable=['ner', 'textcat', 'parser'])
    chunker = RegexpParser(r"""
        NBAR:
            {<NOUN|PROPN|ADJ>*<NOUN|PROPN>}

        NP:
            {<NBAR>}
            {<NBAR><ADP><NBAR>}
    """)


with open('data.jsonl') as f:
    nb_lines = sum(True for l in f)
    f.seek(0)
    f = tqdm(f, total=nb_lines)

    f = grouper(f, 100)
    with open('data_with_extracted_keywords.jsonl', 'w') as g:
        with Pool(6, initializer=init_worker) as p:
            f = p.imap_unordered(process_many, f)
            for group in f:
                for d in group:
                    if not d:
                        continue
                    g.write(d)
