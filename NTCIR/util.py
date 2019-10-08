"""How to introduce the dataset in the slides ???
Change the example for one of NYTime

How do models generalize on other dataset ANNEX
Do model generate or extract ?"""


from collections import Counter
from tqdm import tqdm
import json
import os
import nltk
stem = nltk.stem.PorterStemmer().stem
lts = lambda x: [stem(t) for t in nltk.word_tokenize(x.lower())]
ltsj = lambda x: ' '.join(map(stem, nltk.word_tokenize(x.lower())))
tsj = ltsj

ntcir_datasets = ['ntc2-e1k', 'ntc1-e1', 'ntc2-e1g']
methods = [
    'copy_less-012a145',
]
data = {}


def compute_cleaned_ref_one(args):
        id_, kws, max_ = args
        cleaned = []
        tmp = []
        for kw in kws:
            # for each keyphrase
            if max_ and len(cleaned) >= max_:
                continue
            t = [set(lts(v)) for v in kw]
            if any(any(k - v == set() for v in t) for k in tmp):
                continue
            tmp += t
            cleaned.append(kw)
        return id_, cleaned


def compute_cleaned_ref(candidates, max_=None, process=6):

    cleaned_candidates = {}

    with Pool(process) as p:
        processed = p.imap_unordered(
            compute_cleaned_ref_one,
            ((k, v, max_) for k, v in candidates.items()))
        for id_, cleaned in tqdm(processed):
            # for each document
            cleaned_candidates[id_] = cleaned

    return cleaned_candidates


def tsj_input(jsonl_file):
    data = {}
    with open(jsonl_file) as f:
        for line in tqdm(f):
            # Read, tokenize and stem data
            og_data = json.loads(line)
            doc_id = og_data['id']
            og_data = ' . '.join([og_data['title'], og_data['abstract']])
            og_data = ltsj(og_data)
            data[doc_id] = og_data
    return data


from multiprocessing import Pool


def split_abs_prs_one(args):
    k, doc_cand, og_doc = args
    pres = [[v for v in kp if ltsj(v) in og_doc] for kp in doc_cand]
    pres = [kp for kp in pres if kp]

    abse = [[v for v in kp if ltsj(v) not in og_doc] for kp in doc_cand]
    abse = [kp for kp in abse if kp]
    return k, pres, abse


def split_abs_prs(candidates, og_data, process=6):
    pres, abse = {}, {}

    def gen(data):
        return ((k, candidates[k], d) for k, d in data
                if k in candidates)

    with Pool(process) as p:
        splitted = p.imap_unordered(split_abs_prs_one, gen(og_data.items()))
        for k, p, a in tqdm(splitted):
            pres[k] = p
            abse[k] = a

    return pres, abse


def split_corpus(input_file, method):
    doc_path = '/home/gallina/ir-using-kg/data/docs/'
    docs = ['ntc1-e1', 'ntc2-e1g', 'ntc2-e1k']
    docs = [(os.path.join(doc_path, d), d) for d in docs]

    with open(input_file) as f:
        all_cand = json.load(f)

    for p, d in docs:
        print(d)
        with open(p) as f:
            doc_cand = {line[6:-8]: all_cand[line[6:-8]] for line in f if line.startswith('<ACCN>')}

        out_file = '.'.join([d, 'gz', method, 'all', 'json'])
        with open(out_file, 'w') as f:
            json.dump(doc_cand, f, indent=2)


def process_split_abs_prs():
    global ntcir_datasets
    global methods
    global data
    for dataset_name in ntcir_datasets:
        print(dataset_name)
        dataset_file = '/home/gallina/data/datasets/{}.test.jsonl'.format(dataset_name)
        if dataset_file not in data:
            data[dataset_file] = tsj_input(dataset_file)
        for method in methods:
            cand_file = '/home/gallina/ir-using-kg/data/keyphrases/beam200/{}.gz.{}.beam200.json'.format(dataset_name, method)
            print(cand_file)
            with open(cand_file) as f:
                candidates = json.load(f)

            candidates = compute_cleaned_ref(candidates)

            pres, abse = split_abs_prs(candidates, data[dataset_file], process=9)

            all_ = {k: v[:20] for k, v in candidates.items()}
            pres = {k: v[:20] for k, v in pres.items()}
            abse = {k: v[:20] for k, v in abse.items()}

            out_file = '/home/gallina/ir-using-kg/data/keyphrases/beam200/processed/{}.gz.{}.{{}}.json'.format(dataset_name, method)

            all_out_file = out_file.format('all')
            pres_out_file = out_file.format('pres')
            abs_out_file = out_file.format('abs')

            with open(all_out_file, 'w') as f:
                json.dump(all_, f, indent=2)

            with open(pres_out_file, 'w') as f:
                json.dump(pres, f, indent=2)

            with open(abs_out_file, 'w') as f:
                json.dump(abse, f, indent=2)




def print_sup10(d):
    c = Counter(map(lambda x: len(x)>10, d.values()))
    print({k: (v, v / sum(c.values())) for k, v in c.items()})


def compute_lessthan10elemts(cand_file, corpusname):
    dataset_file = '/home/gallina/data/datasets/{}.test.jsonl'.format(corpusname)
    with open(cand_file) as f:
        candidates = json.load(f)

    cleaned_cand = compute_cleaned_ref(candidates)
    pres, abse = split_abs_prs(cleaned_cand, data[dataset_file])

    print('Cleaned before')
    print_sup10(cleaned_cand)
    print_sup10(pres)
    print_sup10(abse)

    pres, abse = split_abs_prs(candidates, data[dataset_file])
    candidates = compute_cleaned_ref(candidates, max_=20)
    pres = compute_cleaned_ref(pres, max_=20)
    abse = compute_cleaned_ref(abse, max_=20)

    print('Cleaned after')
    print_sup10(candidates)
    print_sup10(pres)
    print_sup10(abse)


def process_split_corpus():
    # Used for NTCIR1+2 files generated via `pke`
    global ntcir_datasets
    global methods
    for method in methods:
        cand_file = '/home/gallina/ake-benchmarking/output/NTCIR1+2/NTCIR1+2.{}.json'.format(method)
        print(cand_file)
        with open(cand_file) as f:
            candidates = json.load(f)

        for dataset_name in ntcir_datasets:
            print(dataset_name)
            dataset_file = '/home/gallina/data/datasets/{}.test.jsonl'.format(dataset_name)

            with open(dataset_file) as f:
                ids = [json.loads(line)['id'] for line in f]

            candidates_tmp = {k: candidates[k] for k in ids}
            candidates_tmp = compute_cleaned_ref(candidates_tmp, max_=20)

            out_file = '/home/gallina/ake-benchmarking/output/NTCIR1+2/{}.gz.pres.{}.json'.format(dataset_name, method)

            print(out_file)
            with open(out_file, 'w') as f:
                json.dump(candidates_tmp, f, indent=2)
