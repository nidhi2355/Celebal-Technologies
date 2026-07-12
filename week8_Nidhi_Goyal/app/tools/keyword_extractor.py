"""
Keyword extraction tool: pulls out the most significant words/phrases
from a block of text using simple frequency + stopword filtering.

No heavy NLP dependency required -- keeps the project lightweight,
in line with the "beginner-friendly" goal in the project description.
"""

import re
from collections import Counter


KEYWORD_SCHEMA = {
    "name": "keyword_extraction",
    "description": "Extracts the top keywords from a piece of text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text to analyze"},
            "top_n": {"type": "integer", "description": "Number of keywords to return", "default": 5},
        },
        "required": ["text"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "keywords": {"type": "array", "items": {"type": "string"}},
        },
    },
}

_STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "and", "or", "but", "if", "then", "so", "of", "in", "on", "at", "to",
    "for", "with", "about", "from", "by", "as", "this", "that", "these",
    "those", "it", "its", "i", "you", "he", "she", "we", "they", "them",
    "me", "my", "your", "his", "her", "our", "their", "can", "could",
    "will", "would", "should", "do", "does", "did", "have", "has", "had",
    "what", "which", "who", "whom", "when", "where", "why", "how",
    "extract", "keywords", "keyword", "please", "give", "find",
}


def run(tool_input: dict) -> dict:
    """
    tool_input: {"text": "<string>", "top_n": <int, optional>}
    returns: {"keywords": [<string>, ...]}
    """
    text = tool_input.get("text", "")
    top_n = tool_input.get("top_n", 5)

    if not text:
        raise ValueError("No text provided to keyword extraction tool.")

    words = re.findall(r"[a-zA-Z']+", text.lower())
    filtered = [w for w in words if w not in _STOPWORDS and len(w) > 2]

    if not filtered:
        return {"keywords": []}

    counts = Counter(filtered)
    top_keywords = [word for word, _ in counts.most_common(top_n)]

    return {"keywords": top_keywords}
