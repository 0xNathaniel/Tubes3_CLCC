from collections import deque
from typing import List, Dict, Optional

# Main Aho-Corasick function to be called

def aho_corasick(text: str, keywords: List[str]) -> List[int]:
    patterns = [keyword.lower() for keyword in keywords]
    
    # Build trie structure from all patterns
    root = build_trie(patterns)
    # Build failure links for efficient backtracking
    build_failure_links(root)
    
    matches = search(text, root)
    
    # Count matches for each keyword
    results = [0] * len(keywords)
    for match_idx in matches:
        results[match_idx] += 1
    
    return results

# TrieNode data structure for Aho-Corasick algorithm

class TrieNode:
    def __init__(self) -> None:
        self.children: Dict[str, 'TrieNode'] = {}  # Child nodes
        self.failure: Optional['TrieNode'] = None  # Failure link for mismatch
        self.output: List[int] = []  # Pattern indices ending at this node

def build_trie(patterns: List[str]) -> TrieNode:
    """Build trie structure from all patterns"""
    root = TrieNode()
    
    for i, pattern in enumerate(patterns):
        node = root
        # Insert each character of pattern into trie
        for char in pattern:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        # Mark end of pattern with its index
        node.output.append(i)
    
    return root

# Aho-Corasick helper functions

def build_failure_links(root: TrieNode) -> None:
    """Build failure links using BFS for efficient pattern matching"""
    queue = deque()
    
    # Initialize failure links for root's children
    for child in root.children.values():
        child.failure = root
        queue.append(child)
    
    while queue:
        current = queue.popleft()
        
        for char, child in current.children.items():
            queue.append(child)
            
            # Find the longest proper suffix that's also a prefix
            failure = current.failure
            while failure and char not in failure.children:
                failure = failure.failure
            
            if failure and char in failure.children:
                # Set failure link to matching suffix
                child.failure = failure.children[char]
            else:
                # No matching suffix, link to root
                child.failure = root
            
            # Inherit output patterns from failure link
            child.output.extend(child.failure.output)

def search(text: str, root: TrieNode) -> List[int]:
    """Search text for all patterns simultaneously"""
    matches = []
    node = root
    
    for _, char in enumerate(text):
        # Follow failure links until we find a match or reach root
        while node and char not in node.children:
            node = node.failure
        
        if node and char in node.children:
            # Move to next state in automaton
            node = node.children[char]
            
            # Report all patterns that end at current position
            for pattern_idx in node.output:
                matches.append(pattern_idx)
        else:
            # No valid transition, restart from root
            node = root
    
    return matches