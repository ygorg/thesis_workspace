def contains(small, big):
    # Checks whether `small` appear contiguously in `big`
    for i in range(
            len(big) - len(small) + 1):
        match_len = 0
        for j in range(len(small)):
            if big[i + j] == small[j]:
                match_len += 1
            else:
                break
        
        if match_len == len(small):
            # Every elements were found
            return True
    return False


def kw_category(kw, doc):
    if contains(kw, doc):
        return 'P'  # Present
    else:
        abs_words = [w for w in kw if w not in doc]
        if len(abs_words) == 0:
            return 'R'  # Reordered
        elif len(abs_words) < len(kw):
            return 'M'  # Mixed
        elif len(abs_words) == len(kw):
            return 'U'  # Unseen