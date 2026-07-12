"""
Query Analyzer node.

Determines the user's intent using fast rule-based heuristics first
(cheap, deterministic, no API call needed). Falls back to "general"
if nothing matches. This is the piece the project's "Future Enhancements"
section calls out for later replacement with LLM-based classification --
the function signature is kept intentionally simple so that swap is a
drop-in change.
"""

import re
from app.state import AgentState
from app.logger import log_event
import json
from app.llm import get_llm


_MATH_PATTERN = re.compile(r"[-+]?\d+(\.\d+)?\s*[-+*/^%]\s*[-+]?\d+(\.\d+)?")
_MATH_KEYWORDS = re.compile(
    r"\b(calculate|compute|sum|multiply|divide|subtract|add|plus|minus|square root|"
    r"what is|solve)\b",
    re.IGNORECASE,
)
_KEYWORD_TRIGGERS = re.compile(
    r"\b(keyword|keywords|extract|summarize topics|main topics|key terms|"
    r"important words)\b",
    re.IGNORECASE,
)
_INTENT_PROMPT = """You are an intent classifier for an AI agent system with three possible intents:

1. "calculator" - the user wants a mathematical expression evaluated
2. "keyword_extraction" - the user wants keywords/key terms extracted from a block of text (bios, notes, descriptions, articles, paragraphs about a topic)
3. "general" - anything else (questions, conversation, requests for information)

Respond with ONLY a JSON object, nothing else, in this exact format:
{{"intent": "calculator" | "keyword_extraction" | "general", "confidence": <float 0 to 1>}}

Query: {query}
"""


def _classify_with_llm(query: str):
    """Returns (intent, confidence) from the LLM, or (None, None) if the
    call fails for any reason (no API key, rate limit, bad JSON, etc.) --
    this lets the caller fall back to rule-based detection safely."""
    try:
        llm = get_llm(temperature=0.0)
        response = llm.invoke(_INTENT_PROMPT.format(query=query))
        text = response.content.strip().replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)
        intent = parsed.get("intent")
        confidence = float(parsed.get("confidence", 0.7))
        if intent in ("calculator", "keyword_extraction", "general"):
            return intent, confidence
    except Exception:
        pass
    return None, None

def _looks_like_descriptive_text(query: str) -> bool:
    """
    Heuristic for "this is a block of info to analyze" rather than
    "this is a question/chat message to answer".
    """
    stripped = query.strip()
    if "?" in stripped:
        return False  # questions go to general/LLM, not keyword extraction

    word_count = len(stripped.split())
    sentence_count = len([s for s in re.split(r"[.!]+", stripped) if s.strip()])

    # Multiple sentences and a reasonable amount of text -> likely a
    # descriptive paragraph (bio, notes, description) worth summarizing
    # into keywords, rather than a short chat message.
    return sentence_count >= 2 and word_count >= 10


def analyze_query(state: AgentState) -> AgentState:
    query = state["query"]

    # Try LLM-based classification first -- catches implicit cases regex
    # can't (like a bio with no "extract keywords" wording). Falls back
    # to rule-based detection if the LLM call fails for any reason.
    llm_intent, llm_confidence = _classify_with_llm(query)
    if llm_intent:
        log_event(state, "query_analyzer", f"LLM classified intent='{llm_intent}' (confidence={llm_confidence})")
        return {"intent": llm_intent, "intent_confidence": llm_confidence}

    # --- Rule-based fallback (no API key / LLM call failed) ---
    if _MATH_PATTERN.search(query) or _MATH_KEYWORDS.search(query):
        intent = "calculator"
        confidence = 0.9
    elif _KEYWORD_TRIGGERS.search(query):
        intent = "keyword_extraction"
        confidence = 0.85
    elif _looks_like_descriptive_text(query):
        intent = "keyword_extraction"
        confidence = 0.6
    elif query.strip():
        intent = "general"
        confidence = 0.5
    else:
        intent = "unknown"
        confidence = 0.0

    log_event(state, "query_analyzer", f"Rule-based fallback intent='{intent}' (confidence={confidence})")
    return {"intent": intent, "intent_confidence": confidence}