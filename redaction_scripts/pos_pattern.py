import util
import json
from collections import Counter, defaultdict
import spacy
from tqdm import tqdm

#l, c = 'fr_core_web_sm', 'TermITH-Eval'
l, c = 'en_core_wbe_sm', 'KP20k'

nlp = spacy.load(l)

with open(util.get_ref(c)) as f:
    ref = json.load(f)
    kws = Counter(v for d in ref.values() for k in d for v in k)
    kws = [(k, v) for k, v in kws.items() if k]

sp_out = list(tqdm(nlp.pipe(kws, as_tuples=True, n_process=5, disable=['ner', 'parser'])))
preproc = [(tuple(t.pos_ for t in r[0]), r[0].text, r[1]) for r in sp_out]

pattern = defaultdict(list)
for p in preproc:
    pattern[p[0]].append(p)
top_pattern = sorted(pattern, key=lambda x: len(pattern[x]))

to_choose = [sorted(((f, t) for _, t, f in pattern[p] if f < 15), reverse=True)[:15] for p in top_pattern]