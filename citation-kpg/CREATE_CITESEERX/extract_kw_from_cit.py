import os
import re
import json
import nltk
import argparse
import itertools
from itertools import chain
from collections import Counter
from multiprocessing import Pool

import spacy
from tqdm import tqdm
from nltk import RegexpParser
from more_itertools import grouper


def merge_compounds(d):
    """ Merge compounds to be one token

    A compound is two tokens separated by a hyphen when the tokens are right next to the hyphen

    d (spacy.Doc): Document
    Returns: spacy.Doc

    > [t.text for t in nlp('peer-to-peer-to-peer')]
    ['peer', '-', 'to', '-', 'peer', 'to', '-', 'peer']
    > [t.text for t in merge_compounds(nlp('peer-to-peer-to-peer'))]
    ['peer-to-peer-to-peer']
    """
    # Returns beginning and end offset of spacy.Token
    offsets = lambda t: (t.idx, t.idx+len(t))

    # Identify the hyphens
    # for each token is it a hyphen and the next and preceding token are right next to the hyphen
    spans = [(i-1, i+1) for i in range(len(d))
             if i != 0 and i < len(d) - 1 and d[i].text == '-' and \
                offsets(d[i-1])[1] == offsets(d[i])[0] and \
                offsets(d[i+1])[0] == offsets(d[i])[1]
            ]
    # merging spans to account for multi-compound terms
    merged = []
    for i, (b, e) in enumerate(spans):
        # if the last spans ends when the current span begins,
        # merge those
        if merged and b == merged[-1][1]:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((b, e))

    # Merge the spacy Doc compute the span beforehand as merging changes the indexation
    to_merge = [d[b:e+1] for b, e in merged]
    for span in to_merge:
        # also computing the lemma (but it will be overwritten)
        span.merge(lemma=''.join(t.lemma_ for t in span))
    return d

def grammar_selection(doc, chunker):
    # initialize chunker
    tuples = [((i, e.text), e.pos_) for i, e in enumerate(doc)]
    tree = chunker.parse(tuples)
    acc = []
    # find candidates
    for subtree in tree.subtrees():
        if subtree.label() == 'NP':
            acc.append((subtree.leaves()[0][0][0], ' '.join(l[0][1] for l in subtree.leaves())))
    return acc


def get_sent(d):
    return [s for s in nltk.sent_tokenize(d) if '=-=' in s]

et_al_p = re.compile(r'\bet al\.')
def pretreat_ctxt(ctxt):
    # Preprocess, remove markup and return sentence containing the citation markup.
    #ctxt = re.sub(r'\d+(\s*,\s*\d+)*', '<D>', ctxt[1])
    ctxt = et_al_p.sub(r'et al', ctxt[1])
    ctxt = ctxt.replace('[', ' [').replace(']', '] ')
    ctxt = ctxt.replace('-=-', '')
    doc = get_sent(ctxt)
    if not doc:
        return None
    doc = doc[0]
    marker_offset = doc.find('=-=')
    if marker_offset < 0:
        print(doc)
        input()
        return None
    doc = doc.replace('=-=', '')
    return doc, marker_offset



# Keep if all words are not one character
word_len = lambda k: not all(len(t) == 1 for t in k.split(' '))
# Keep if at least 70% of char are letters (if 3 or less char, keep if at least one letter)
letter_ratio = lambda k: sum(c.isalpha() or c == ' ' for c in k) / len(k) > (0.7 if len(k) > 3 else 0)
# Keep if has no special characters (math symbols, russian script, ...)
spe_char = lambda k: all(ord(' ') <= ord(c) <= ord('z') for c in k)
# Keep if has less than 6 words
len_kw = lambda k: len(k.split(' ')) < 7
# Keep if not comprises a citation
et_al_ = re.compile(r'\bet al\b')
et_al = lambda k: not et_al_.search(k)
all_filt = [spe_char, word_len, letter_ratio, len_kw, et_al]


def groupby(iterable, key=lambda x: x[0]):
    iterable = sorted(iterable, key=key)
    iterable = itertools.groupby(iterable, key=key)
    return [(k, list(v)) for k, v in iterable]

def process_one(line, nlp, chunker):
    d = json.loads(line)
    if 'keyword' in d:
        d['author_keyword'] = d['keyword']
    if not letter_ratio(d['title'] + ' ' + d['abstract']):
        # Document have more than 70% of punctutaion
        return None
    # Pre-treat and compute offset of marker
    ctxt = map(pretreat_ctxt, d['ctxt'])
    ctxt = filter(None, ctxt)
    ctxt = nlp.pipe(ctxt, as_tuples=True, batch_size=50)
    kws = []
    for tokens, marker_offset in ctxt:
        # For each tokenized context
        cands = grammar_selection(tokens, chunker)
        # Convert marker's offset to token index in order to compute the
        #  distance of candidate to the marker (that is now removed)
        tmp = [i for i, t in enumerate(tokens) if t.idx >= marker_offset]
        tmp = tmp[0] if tmp else len(tokens)
        cands = [(k, abs(i - tmp) / len(tokens)) for i, k in cands]
        # Keep one of each candidate (closest to the marker)
        cands = [(k, min(e[1] for e in v)) for k, v in groupby(cands)]
        kws.append(cands)

    kws = [k for c in kws for k in c]  # Flatten kw list
    kws = ((k, min(e[1] for e in v), len(v)) for k, v in groupby(kws))  # Count keyword
    kws = [(k, p, f) for k, p, f in kws if f > 1]  # Remove keyword occuring once
    # Filter out noisy keywords
    for filt in all_filt:
        kws = filter(lambda x: filt(x[0]), kws)
    kws = filter(lambda x: ';' not in x[0], kws)
    kws = list(kws)
    kept_kws = []
    indexes = sorted(set(e[2] for e in kws), reverse=True)
    # Add keywords starting with the closer to the marker, with 10 maximum
    for i in indexes:
        to_add = {k: p for k, p, f in kws if f == i}
        #to_add = to_add.keys()
        to_add = sorted(to_add, key=to_add.get)
        if len(to_add) > 10:
            to_add = to_add[:10]
        kept_kws += to_add
        if len(kept_kws) > 10:
            break
    d['keyword'] = ';'.join(kept_kws)

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
    nlp.add_pipe(merge_compounds)
    chunker = RegexpParser(r"""
        NBAR:
            {<NOUN|ADJ|PROPN>*<NOUN|PROPN>}

        NP:
            {<NBAR>}
            {<NBAR><ADP><NBAR>}
    """)

if __name__ == '__main__':
    def arguments():
        parser = argparse.ArgumentParser(description='Extract synthetic keyphrases from "ctxt" in jsonl file. Outputs a jsonl file with "keyword".')
        parser.add_argument('data', type=str,
            help='Data file.')
        parser.add_argument('--parallel', type=int,
            help='Number of thread to use. (Default: 0)', default=0)
        parser.add_argument('--batch_size', type=int,
            help='Number of document per thread. (Default: 50)', default=50)
        return parser.parse_args()
    args = arguments()

    here = os.path.dirname(__file__) or '.'
    input_file = args.data
    if '.jsonl' not in args.data:
        args.data += '.jsonl'
    output_file = args.data.replace('.jsonl', '_w_synth_kw.jsonl')
    parallel = args.parallel
    batch_size = args.batch_size

    with open(input_file) as f:
        #nb_lines = sum(True for l in f)
        #f.seek(0)
        nb_lines = 355869
        f = tqdm(f, total=nb_lines)
        f = grouper(f, batch_size)
        
        ctxts = []
        with open(output_file, 'w') as g:
            if parallel >= 2:
                p = Pool(parallel, initializer=init_worker)
                f = p.imap_unordered(process_many, f)
            else:
                init_worker()
                f = map(process_many, f)
            f = chain.from_iterable(f)
            f = filter(None, f)
            for d in f:
                g.write(d)
            if parallel >= 2:
                p.close()

