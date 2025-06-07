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
    
    # Search for pattern starting from different positions in text
    while start_pos <= len(text) - len(pattern):
        match_pos = bm_match_single(text[start_pos:], pattern)
        
        if match_pos == -1:
            break
        
        count += 1
        # Move to next potential match position
        start_pos = start_pos + match_pos + 1
    
    return count

def bm_match_single(text: str, pattern: str) -> int:
    # Build last occurrence table for bad character heuristic
    last = build_last_occurrence_table(pattern)
    n, m = len(text), len(pattern)
    
    if m > n:
        return -1 
    
    # Start from the end of pattern (Boyer-Moore's key optimization)
    i = m - 1  # Text index
    j = m - 1  # Pattern index
    
    while i <= n - 1:
        if pattern[j] == text[i]:
            if j == 0:
                # Complete match found, return starting position
                return i 
            else:
                # Characters match, move backwards
                i -= 1
                j -= 1
        else:
            # Mismatch occurred - apply bad character heuristic
            char_index = ord(text[i]) if ord(text[i]) < 128 else 0
            lo = last[char_index] 
            
            # Skip positions based on bad character rule
            i = i + m - min(j, 1 + lo)
            j = m - 1  # Reset pattern index to end
    
    return -1

def build_last_occurrence_table(pattern: str) -> List[int]:
    """Build table storing last occurrence of each character in pattern"""
    last = [-1] * 128  # ASCII table size
    
    # Record the rightmost position of each character
    for i in range(len(pattern)):
        last[ord(pattern[i])] = i
    
    return last