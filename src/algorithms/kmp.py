from typing import List

# Main KMP function to be called

def kmp(text: str, keywords: List[str]) -> List[int]:    
    """Search for multiple keywords in text using KMP algorithm"""
    results = []
    for keyword in keywords:
        keyword_lower = keyword.lower()
        count = kmp_search(text, keyword_lower)
        results.append(count)
    
    return results

# KMP Algorithm

def kmp_search(text: str, pattern: str) -> int:
    """Find all occurrences of pattern in text using KMP algorithm"""
    n, m = len(text), len(pattern)
    if m == 0:
        return 0
        
    # Build the LPS (Longest Prefix Suffix) array for the pattern
    lps = compute_border(pattern)
    count = 0
    i = j = 0  # i for text index, j for pattern index
    
    while i < n:
        # Characters match, advance both pointers
        if text[i] == pattern[j]:
            i += 1
            j += 1
        
        # Complete pattern found
        if j == m:
            count += 1
            # Use LPS to skip redundant comparisons
            j = lps[j - 1]
        # Mismatch occurred
        elif i < n and text[i] != pattern[j]:
            if j != 0:
                # Use LPS to avoid re-checking already matched prefix
                j = lps[j - 1]
            else:
                # No prefix to skip, move to next character in text
                i += 1
                
    return count

# KMP Border function

def compute_border(pattern: str) -> List[int]:
    """Compute LPS (Longest Prefix Suffix) array for KMP algorithm"""
    m = len(pattern)
    lps = [0] * m  # LPS array initialization
    length = 0     # Length of previous longest prefix suffix
    i = 1          # Start from second character
    
    while i < m:
        # Current character matches with character at 'length' position
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            # Mismatch occurred
            if length != 0:
                # Use previously computed LPS value to backtrack
                length = lps[length - 1]
            else:
                # No proper prefix exists, set LPS to 0
                lps[i] = 0
                i += 1
    return lps