# Main KMP function to be called

def kmp(text, keywords):    
    results = []
    for keyword in keywords:
        keyword_lower = keyword.lower()
        count = kmp_search(text, keyword_lower)
        results.append(count)
    
    return results

# KMP Algorithm

def kmp_search(text, pattern):
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
        
    lps = compute_border(pattern)
    count = 0
    i = j = 0
    
    while i < n:
        if text[i] == pattern[j]:
            i += 1
            j += 1
        
        if j == m:
            count += 1
            j = lps[j - 1]
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
                
    return count

# KMP Border function

def compute_border(pattern):
    m = len(pattern)
    lps = [0] * m
    length = 0
    i = 1
    
    while i < m:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps