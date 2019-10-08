import os
import json
from copy import deepcopy
from multiprocessing import Pool

import nltk
from tqdm import tqdm


stem = nltk.stem.PorterStemmer().stem
# Tokenize, stem, join
tsj = lambda s: ' '.join(stem(t) for t in nltk.word_tokenize(s))


def compute_pres_abs_kp(line, lower=True, stem=False):
    content = line['title'] + ' . ' + line['abstract']
    content = content.lower() if lower else content
    content = tsj(content) if stem else content
    pres, abse = [], []
    keyword = line['keyword']

    for i, kp in enumerate(keyword):
        p_acc, a_acc = [], []
        for v in kp:
            og_v = v
            v = v.lower() if lower else v
            v = tsj(v) if stem else v
            if v in content:
                p_acc.append(og_v)
            else:
                a_acc.append(og_v)
        if p_acc:
            pres.append(p_acc)
        if a_acc:
            abse.append(a_acc)
    return pres, abse


def kplst2str(kws):
    # Convert keyphrase List[List[str]] to str
    return ';'.join(','.join(k) for k in kws)


def kpstr2lst(kws):
    # Convert keyphrase str to List[List[str]]
    return [kp.split(',') for kp in kws.split(';')]


if __name__ == '__main__':
    import argparse

    def arguments():
        parser = argparse.ArgumentParser(description='Create absent and present reference keyphrases. Creates "../abs/`file`" and "../prs/`file`".')
        parser.add_argument('-p', '--parallel', type=int, default=1, metavar='P',
                            help='Run `P` workers processes to speed up process(Default: 1)')
        parser.add_argument('-s', '--stem', action='store_true',
                            help='Compute present and absent keyphrases using stemming')
        parser.add_argument('FILE', type=argparse.FileType('r'),
                            help='Input file in `.jsonl` format. With ("title" and/or "abstract") and "keyword" fields')
        args = parser.parse_args()
        return args

    args = arguments()
    in_file = args.FILE

    def process(line):
        line = json.loads(line)
        line['keyword'] = kpstr2lst(line['keyword'])
        p, a = compute_pres_abs_kp(line, stem=True)
        line['keyword'] = kplst2str(a)
        line_a = line
        line_p = deepcopy(line)
        line_p['keyword'] = kplst2str(p)
        return json.dumps(line_p) + '\n', json.dumps(line_a) + '\n'

    prs_ref = {}
    abs_ref = {}

    d, b = os.path.split(in_file)
    prs_outfile = os.path.join([b, '..', 'pres', b])
    abs_outfile = os.path.join([b, '..', 'abs', b])
    os.makedirs(os.dirname(prs_outfile), exist_ok=True)
    os.makedirs(os.dirname(abs_outfile), exist_ok=True)

    with open(prs_outfile, 'w') as prs_file:
        with open(abs_outfile, 'w') as abs_file:
            with Pool(args.parallel) as pool:
                for prs_line, abs_line in tqdm(pool.imap_unordered(process, in_file)):
                    prs_file.write(prs_line)
                    abs_file.write(abs_line)
