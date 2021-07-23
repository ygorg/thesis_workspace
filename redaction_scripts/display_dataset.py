import json

def aaa(data, ref, output, n=5, len_doc=None):
    with open(ref) as f:
        ref = json.load(f)
    with open(output) as f:
        output = json.load(f)
    with open(data) as f:
        data = [json.loads(l) for l in f]
    for d in data:
        print(d['title'][:len_doc])
        print(d['abstract'][:len_doc])
        print([v for k in ref[d['id']] for v in k])
        print([v for k in output[d['id']][:n] for v in k])
        input()

aaa('../data/datasets/KPCrowd.test.jsonl', util.get_ref('KPCrowd'), '../ake-benchmarking/output/KPCrowd/KPCrowd.CopyRNN_News.json')