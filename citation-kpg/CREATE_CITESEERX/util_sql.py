cdef int count_matching_parenthesis(unsigned char[:] z):
    cdef int acc = 0;
    cdef int open_count = 0
    cdef bint in_str = False
    cdef bint escape = False
    for c in z:
        if escape:
            escape = False
        else:
            if in_str:
                if c == '\'':
                    in_str = not in_str
                elif c == '\\':
                    escape = True
            else:
                if c == '(':
                    open_count += 1
                elif c == ')':
                    open_count -= 1
                    if open_count == 0:
                        acc += 1
                elif c == '\'':
                    in_str = not in_str
                elif c == '\\':
                    escape = True
        #print(c, open_count, str(in_str)[0], str(escape)[0], acc)
    return acc

paren_parity("('lal\\ala'), ('la(lo'), (), ('l\\'abeille est (moche).')")


# Count number of rows to be inserted
from tqdm import tqdm
with open('papers.sql') as f:
    acc = []
    for l in tqdm(f, miniters=2000):
        if 'INSERT' not in l:
            continue
        acc.append(count_matching_parenthesis(l))
        #acc.append(l.count("),('") + 1)
        if len(acc) % 2000 == 0:
            print(len(acc), sum(acc))
    print(len(acc), sum(acc))

# Find missing ids
from tqdm import tqdm
from collections import Counter

with open('papers_id.txt') as f:
    l_got_ids = [l.strip() for l in f]
got_ids = set(l_got_ids)
assert len(l_got_ids) == len(got_ids)

missing_ids = set()
with open('papers.sql') as f:
    for l in tqdm(f, miniters=2000):
        if 'INSERT' not in l:
            continue
        # Split line into insert tuples
        rows = l.replace('INSERT INTO `papers` VALUES (', '').split('),(')
        # Extract ids (1st element)
        l_row_ids = [r.replace("'", '').split(',')[0] for r in rows]
        row_ids = set(l_row_ids)
        if len(l_row_ids) != len(row_ids):
            print(Counter(l_row_ids).most_common(3))
            print(l)
            input('Appuyez sur une touche')

        missing_ids |= row_ids - got_ids
        got_ids -= row_ids


# Split file in multiple files
n_split = 10000
with open('citations.sql') as f:
    g = open('citations.{}-{}.sql'.format(0, n_split), 'w')
    g.write('LOCK TABLES `citations` WRITE;\n')
    i = 0
    for l in f:
        if 'INSERT' in l:
            g.write(l)
            i += 1
        if i % n_split == 0 and i != 0:
            g.write('UNLOCK TABLES;\n')
            g.close()
            g = open('citations.{}-{}.sql'.format(i, i+n_split), 'w')
    g.write('UNLOCK TABLES;\n')
    g.close()

# pv citations.0-10000.sql | mysql -u root -p citeseerx