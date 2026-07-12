from .calculator import run as run_calculator, extract_expression, CALCULATOR_SCHEMA
from .keyword_extractor import run as run_keyword_extraction, KEYWORD_SCHEMA

# Registry mapping tool name -> callable. The tool_executor node uses this
# to dispatch dynamically instead of an if/elif chain, so adding a new tool
# later (web search, RAG, etc.) only means adding one line here.
TOOL_REGISTRY = {
    "calculator": run_calculator,
    "keyword_extraction": run_keyword_extraction,
}

TOOL_SCHEMAS = {
    "calculator": CALCULATOR_SCHEMA,
    "keyword_extraction": KEYWORD_SCHEMA,
}

__all__ = [
    "run_calculator",
    "run_keyword_extraction",
    "extract_expression",
    "TOOL_REGISTRY",
    "TOOL_SCHEMAS",
]
