import json
import random
from glob import glob
from itertools import chain
from collections import defaultdict

import nltk
import seaborn as sns

sent_tok = nltk.tokenize.punkt.PunktSentenceTokenizer().span_tokenize
try:
    word_tok = nltk.tokenize._treebank_word_tokenizer.span_tokenize
except:
    word_tok = nltk.tokenize.TreebankWordTokenizer().span_tokenize
stem = nltk.stem.PorterStemmer().stem


def span_tok_stem(text):
    # Compute word offsets
    tok = [(b + w_b, b + w_e) for b, e in sent_tok(text)
           for w_b, w_e in word_tok(text[b:e])]
    # Compute stem
    tok = [(b, e, stem(text[b:e].lower()))
           for b, e in tok]
    return tok


def create_colors(nb):
    tmp = list(sns.color_palette('husl', nb))
    names = {f'mycolor{i}': ', '.join(map(str, v)) for i, v in enumerate(tmp)}
    latex_def = '\n'.join(
        f'\\definecolor{{{k}}}{{rgb}}{{{v}}}' for k, v in names.items()
    )
    return list(names.keys()), latex_def


def add_around_str(str, b, e, f):
    return str[:b] + f(str[b:e]) + str[e:]


def apply_tag(text, tok_text, voc, palette):
    for b, e, s in tok_text[::-1]:
        if s in voc:
            tag_func = lambda x: f'\\textcolor{{{palette[voc[s]]}}}{{{x}}}'
            text = add_around_str(text, b, e, tag_func)
    return text


def to_latex(doc, ref=None):
    ref = None
    t = doc['title']
    a = doc['abstract']
    if ref is None:
        ref = [kws.split(',') for kws in doc['keyword'].split(';')]
    t_tok = span_tok_stem(t)
    a_tok = span_tok_stem(a)
    r_tok = [[(v, span_tok_stem(v)) for v in kw] for kw in ref]

    src_voc = set(t[2] for t in chain(t_tok, a_tok))
    ref_voc = set(t[2] for kw in r_tok for _, v in kw for t in v)

    prs_voc = {w: i for i, w in enumerate(src_voc & ref_voc)}

    palette, defs = create_colors(len(prs_voc))

    p_t = apply_tag(t, t_tok, prs_voc, palette)
    p_a = apply_tag(a, a_tok, prs_voc, palette)

    p_r = [[apply_tag(v, tok, prs_voc, palette).replace(' ', '~')
            for v, tok in kw] for kw in r_tok]

    export_ = defs + '''
\\begin{figure*}
    \\centering
    %\\centerfloat
    \\resizebox{0.98\\textwidth}{!}{%
    \\begin{tabular}{|p{1.3\\textwidth}|}
    \\textbf{''' + p_t + '''}

    \\vspace{0.5em}

    ''' + p_a + '''

    \\vspace{0.5em}

    \\textbf{Termes-clés de référence:} ''' + ', '.join(', '.join(k) for k in p_r) + '''

    \\end{tabular}%
    }
    \\caption{(id: {\\tiny''' + doc['id'] + '''})). Les mots composants termes-clés présent dans le document sont soulignés.}
    \\label{fig:_}
\\end{figure*}'''
    return export_


if __name__ == '__main__':
    import argparse

    def arguments():
        parser = argparse.ArgumentParser(
            description='Keyphrase extraction performance evaluation script.')
        parser.add_argument(
            'input', type=argparse.FileType('r'),
            help='path to file containing jsonl')
        parser.add_argument(
            '-i', required=False, type=str,
            help='id of document to export')
        return parser.parse_args()

    args = arguments()


    # Load documents with 
    f = map(json.loads, args.input)
    docs = {l['id']: l for l in f if l['id']}
    if args.i:
        id_ex = args.i
    else:
        id_ex = random.sample(list(docs), 1)[0]

    print(to_latex(docs[id_ex]))

"""
# Find document that have all kind of fine grained abs/prs
glob_path_files = '/tmp/ake/_home_gallina_ake-datasets_datasets_KP20k_references_test.author.stem.json.*'
# load all fine grained files
res = defaultdict(dict) 
for f in glob(glob_path_files): 
    with open(f) as f: 
        id_ = f.name.split('.')[-1] 
        tmp = json.load(f) 
        for k, v in tmp.items(): 
            res[k][id_] = v
# filter them
refs = {k: v for k, v in res.items() if all(map(bool, v.values()))}
"""