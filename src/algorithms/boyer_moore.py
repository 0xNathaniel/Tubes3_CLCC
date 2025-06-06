from typing import List

# Main Boyer-Moore function to be called

def boyer_moore(text: str, keywords: List[str]) -> List[int]:
    results = []
    for keyword in keywords:
        keyword_lower = keyword.lower()
        count = bm_search_all_occurrences(text, keyword_lower)
        results.append(count)
    
    return results

# Boyer-Moore Algorithm

def bm_search_all_occurrences(text: str, pattern: str) -> int:
    if not pattern:
        return 0
        
    count = 0
    start_pos = 0
    
    while start_pos <= len(text) - len(pattern):
        match_pos = bm_match_single(text[start_pos:], pattern)
        
        if match_pos == -1:
            break
        
        count += 1
        start_pos = start_pos + match_pos + 1
    
    return count

def bm_match_single(text: str, pattern: str) -> int:
    last = build_last_occurrence_table(pattern)
    n, m = len(text), len(pattern)
    
    if m > n:
        return -1 
    
    i = m - 1  
    j = m - 1 
    
    while i <= n - 1:
        if pattern[j] == text[i]:
            if j == 0:
                return i 
            else:
                i -= 1
                j -= 1
        else:
            char_index = ord(text[i]) if ord(text[i]) < 128 else 0
            lo = last[char_index] 
            
            i = i + m - min(j, 1 + lo)
            j = m - 1  
    
    return -1

def build_last_occurrence_table(pattern: str) -> List[int]:
    last = [-1] * 128
    
    for i in range(len(pattern)):
        last[ord(pattern[i])] = i
    
    return last