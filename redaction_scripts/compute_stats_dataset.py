# A VERIFIER
import os
import json
import glob
# from collections import Counter

from tqdm import tqdm
# import matplotlib.pyplot as plt
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from pke.readers import MinimalCoreNLPReader


def tokenize(s):
    """Tokenize an input text."""
    return word_tokenize(s)


def lowercase_and_stem(_words):
    """lowercase and stem sequence of words."""
    return [PorterStemmer().stem(w.lower()) for w in _words]


def contains(subseq, inseq):
    return any(inseq[pos:pos + len(subseq)] == subseq
               for pos in range(0, len(inseq) - len(subseq) + 1))


def flatten_list(a):
    return [item for sublist in a for item in sublist]


def pmru_uw(tok_title, tok_text, tok_kps):
    """Distribute keyphrases within PMRU categories."""

    p, r, m, u = [], [], [], []
    absent_words = set()

    # loop through the keyphrases
    for j, kp in enumerate(tok_kps):

        # if kp is present
        if contains(kp, tok_title) or contains(kp, tok_text):
            p.append(j)

        # if kp is considered as absent
        else:

            # find present and absent words
            present_words = [w for w in kp if w in tok_title or w in tok_text]
            absent_words.update([
                w for w in kp
                if w not in tok_title and w not in tok_text])

            # if "all" words are present
            if len(present_words) == len(kp):
                r.append(j)
            # if "some" words are present
            elif len(present_words) > 0:
                m.append(j)
            # if "no" words are present
            else:
                u.append(j)

    uw = len(absent_words) / len(set(flatten_list(tok_kps)))
    return p, r, m, u, uw


per_dataset = {}

references_path = glob.glob('ake-datasets/datasets/*/references/*test*.json')
# references_path = [r for r in references_path if 'KPTimes' in r]
for path in tqdm(references_path, position=0):

    split_path = path.split(os.sep)
    ref_name = os.path.join(*split_path[2:5:2])
    ref_name = ref_name.replace('.json', '').replace('test.', '')
    dataset_name = split_path[2]

    if ref_name in per_dataset.get(dataset_name, [''])[-1]:
        continue

    with open(path) as f:
        r = json.load(f)

    # path to test and train documents
    path_to_test = os.path.join(*split_path[:-2], 'test', '*.xml')
    path_to_train = os.path.join(*split_path[:-2], 'train', '*.xml')
    test_documents = glob.glob(path_to_test)

    nb_doc_test = len(test_documents)
    if dataset_name not in per_dataset:
        # Nb doc
        nb_doc_train = len(glob.glob(path_to_train))

    # nb mc par document
    with open(path) as f:
        ref = json.load(f)

    if len(ref) != nb_doc_test:
        print(f'{ref_name} has {len(ref)} doc whereas '
              f'there is {nb_doc_test} documents...')
        print('Skipping this ref')
        continue

    # Nb kw per doc (on the test set)
    nb_kw_doc = sum(len(v) for v in ref.values()) / len(ref)

    # Nb words per doc (on the test set)
    len_docs = 0
    nb_prs = []
    nb_kw = []
    for p in tqdm(test_documents, desc=ref_name, position=1):
        xml_parser = MinimalCoreNLPReader()
        d = xml_parser.read(p)
        stems = lowercase_and_stem([w for s in d.sentences for w in s.words])
        len_docs += len(stems)

        keyphrases = ref[os.path.basename(p).rsplit('.', 1)[0]]
        keyphrases
        if keyphrases:
            tok_kps = [lowercase_and_stem(tokenize(v))
                       for k in keyphrases for v in k]
            out = pmru_uw(stems, [], tok_kps)
            nb_prs.append(len(keyphrases) - len(out[0]))
            nb_kw.append(len(keyphrases))
    len_docs /= nb_doc_test
    nb_prs_macro = sum(nb_prs) / sum(nb_kw)
    nb_prs_micro = sum(a / n for a, n in zip(nb_prs, nb_kw)) / len(nb_prs)

    if dataset_name not in per_dataset:
        per_dataset[dataset_name] = [nb_doc_train, nb_doc_test, len_docs, {}]
    per_dataset[dataset_name][-1].update({
        ref_name: (nb_kw_doc, nb_prs_macro, nb_prs_micro)})


dataset2type = {
    'KDD': 'abstract',
    'NUS': 'full',
    'WWW': 'abstract',
    'Inspec': 'abstract',
    '500N-KPCrowd': 'news',
    'CSTR': 'full',
    'PubMed': 'full',
    'Citeulike-180': 'full',
    'WikinewsKeyphrase': 'news',
    'DUC-2001': 'news',
    'ACM': 'full',
    '110-PT-BN-KP': 'news',
    'TermITH-Eval': 'abstract',
    'SemEval-2010': 'full',
    'ACM-abstract': 'abstract',
    'SemEval-2010-abstract': 'abstract',
    'KP20k': 'abstract',
    'KPTimes': 'news',
    'TALN-Archives-fr': 'abstract',
    'TALN-Archives-en': 'abstract'
}


df = pd.DataFrame([
    (k, r.replace(k+'/', ''), nb_tr, nb_te, nb_wo, stat[0], stat[1]*100, stat[2]*100)
    for k, (nb_tr, nb_te, nb_wo, rr) in per_dataset.items()
    for r, stat in rr.items()
], columns=['dataset', 'ref', '#Entr.', '#Test', '#mots', '#mc', '%abs_ma', '%abs_mi'])

df['type'] = df['dataset'].map(lambda x: dataset2type.get(x, ''))
df = df.sort_values(['type', 'dataset', 'ref'])
df = df.round(1)
df = df[['dataset', '#Entr.', '#Test', '#mots', '#mc', '%abs', 'ref']]
print(df.to_latex(index=False))