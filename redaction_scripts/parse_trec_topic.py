import re

topics = 'data/acm-cr/topis/acm-cr-30.topics'
# topics = 'data/ntcir-2/topics/topic-e0101-0149.title+desc+narr.trec'

with open(topics) as f:
    data = []
    
    in_top = in_desc = in_narr = False
    desc = None
    id_ = None
    for i, line in enumerate(f):
        line = line.strip()
        if line.startswith('<top>'):
            in_desc = in_narr = False
            in_top = True
        elif line.startswith('<title>'):
            in_desc = in_narr = False
            continue
        elif line.startswith('<num>'):
            in_desc = in_narr = False
            id_ = line.split(' ')[2]
        elif line.startswith('<narr>'):
            in_desc = False
            in_narr = True
            continue
        elif line.startswith('<desc>'):
            in_desc = True
            in_narr = False
            desc = ''
        elif line.startswith('</top>'):
            in_desc = in_narr = False
            desc = re.sub(r'\[\d+(, \d+)*\]', '', desc)
            data.append(len(tokenize(desc)))
            print(desc)
            in_top = False
            desc = None
            id_ = None
        elif not line:
            continue
        elif in_desc:
            desc += line
        elif in_narr:
            continue
        else:
            raise Exception(f'Parsing error at line {i}, {id_}. in_top: {in_top}, in_desc {in_desc}, "{line}"')

print(sum(data) / len(data))