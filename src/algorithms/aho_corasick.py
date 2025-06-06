from collections import deque
from typing import List, Dict, Optional

# Main Aho-Corasick function to be called

def aho_corasick(text: str, keywords: List[str]) -> List[int]:
    patterns = [keyword.lower() for keyword in keywords]
    
    root = build_trie(patterns)
    build_failure_links(root)
    
    matches = search(text, root)
    
    results = [0] * len(keywords)
    for match_idx in matches:
        results[match_idx] += 1
    
    return results

# TrieNode data structure for Aho-Corasick algorithm

class TrieNode:
    def __init__(self) -> None:
        self.children: Dict[str, 'TrieNode'] = {}
        self.failure: Optional['TrieNode'] = None
        self.output: List[int] = []

def build_trie(patterns: List[str]) -> TrieNode:
    root = TrieNode()
    
    for i, pattern in enumerate(patterns):
        node = root
        for char in pattern:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.output.append(i)
    
    return root

# Aho-Corasick helper functions

def build_failure_links(root: TrieNode) -> None:
    queue = deque()
    
    for child in root.children.values():
        child.failure = root
        queue.append(child)
    
    while queue:
        current = queue.popleft()
        
        for char, child in current.children.items():
            queue.append(child)
            
            failure = current.failure
            while failure and char not in failure.children:
                failure = failure.failure
            
            if failure and char in failure.children:
                child.failure = failure.children[char]
            else:
                child.failure = root
            
            child.output.extend(child.failure.output)

def search(text: str, root: TrieNode) -> List[int]:
    matches = []
    node = root
    
    for _, char in enumerate(text):
        while node and char not in node.children:
            node = node.failure
        
        if node and char in node.children:
            node = node.children[char]
            
            for pattern_idx in node.output:
                matches.append(pattern_idx)
        else:
            node = root
    
    return matches