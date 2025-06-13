import re
from typing import List, Tuple


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings using dynamic programming"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    # Create matrix for dynamic programming
    previous_row = list(range(len(s2) + 1))
    
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, and substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            
            current_row.append(min(insertions, deletions, substitutions))
        
        previous_row = current_row
    
    return previous_row[-1]


def extract_words_with_positions(text: str) -> List[Tuple[str, int]]:
    """Extract words with their positions from text using regex"""
    words = []
    for match in re.finditer(r'\b[a-zA-Z][a-zA-Z0-9+#.-]*\b', text):
        words.append((match.group().lower(), match.start()))
    return words


def extract_words_simple(text: str) -> List[str]:
    """Extract words from text using regex"""
    return re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.-]*\b', text.lower())


def find_fuzzy_matches_sliding_window(text: str, keyword: str, max_dist: int) -> int:
    """Find fuzzy matches using sliding window approach"""
    matches = 0
    keyword_len = len(keyword)
    text_len = len(text)
    
    # Check different window sizes (keyword length ± max_distance)
    min_window = max(1, keyword_len - max_dist)
    max_window = keyword_len + max_dist
    
    for window_size in range(min_window, max_window + 1):
        for i in range(text_len - window_size + 1):
            substring = text[i:i + window_size]
            
            # Skip if substring is part of a larger word (word boundary check)
            if i > 0 and text[i-1].isalnum():
                continue
            if i + window_size < text_len and text[i + window_size].isalnum():
                continue
            
            distance = levenshtein_distance(keyword, substring)
            if distance <= max_dist:
                matches += 1
                # Skip overlapping matches by advancing position
                break
    
    return matches


def find_fuzzy_matches_word_based(text: str, keyword: str, max_dist: int) -> int:
    """Find fuzzy matches by comparing against individual words"""
    words = extract_words_with_positions(text)
    matches = 0
    
    for word, _ in words:
        distance = levenshtein_distance(keyword, word)
        if distance <= max_dist:
            matches += 1
    
    return matches


def find_fuzzy_matches_hybrid(text: str, keyword: str, max_dist: int) -> int:
    """Hybrid approach: word-based first, then sliding window for short keywords"""
    # First, try exact word-based matching
    word_matches = find_fuzzy_matches_word_based(text, keyword, max_dist)
    
    # If no matches found and keyword is short, try sliding window
    if word_matches == 0 and len(keyword) <= 6:
        return find_fuzzy_matches_sliding_window(text, keyword, max_dist)
    
    return word_matches


def calculate_similarity_score(s1: str, s2: str) -> float:
    """Calculate similarity score between two strings (0.0 to 1.0)"""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
        
    max_len = max(len(s1), len(s2))
    distance = levenshtein_distance(s1, s2)
    return 1.0 - (distance / max_len)


def levenshtein_fuzzy_match(text: str, keywords: List[str], max_distance: int = 2) -> List[int]:
    """Main fuzzy matching function using Levenshtein distance"""
    results = []
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Skip empty keywords
        if not keyword_lower:
            results.append(0)
            continue
        
        # Use hybrid approach for best results
        count = find_fuzzy_matches_hybrid(text, keyword_lower, max_distance)
        results.append(count)
    
    return results


def levenshtein_similarity_score(text: str, keywords: List[str], similarity_threshold: float = 0.7) -> List[int]:
    """Find matches using similarity score threshold"""
    results = []
    words_in_text = extract_words_simple(text)
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        matches = 0
        
        for word in words_in_text:
            score = calculate_similarity_score(keyword_lower, word)
            if score >= similarity_threshold:
                matches += 1
        
        results.append(matches)
    
    return results


def fuzzy_match(text: str, keywords: List[str], strategy: str = 'hybrid', 
                max_distance: int = 1, similarity_threshold: float = 0.8) -> List[int]:
    """Main fuzzy matching interface with multiple strategies"""
    if strategy == 'distance':
        return levenshtein_fuzzy_match(text, keywords, max_distance)
    elif strategy == 'similarity':
        return levenshtein_similarity_score(text, keywords, similarity_threshold)
    else:  
        return levenshtein_fuzzy_match(text, keywords, max_distance)