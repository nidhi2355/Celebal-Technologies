"""
Router node.

Two responsibilities, matching the project's "Router" step:
  1. `select_tool` -- a regular node that sets state["selected_tool"]
     and builds the structured tool_input for it.
  2. `route_after_analysis` -- the conditional-edge FUNCTION that
     LangGraph calls to decide which node to go to next. This is what
     makes the graph a directed graph with branching, not a straight line.
"""

from app.state import AgentState
from app.tools import extract_expression
from app.logger import log_event


def select_tool(state: AgentState) -> AgentState:
    intent = state["intent"]
    query = state["query"]

    if intent == "calculator":
        try:
            expression = extract_expression(query)
            tool_input = {"expression": expression}
        except ValueError as e:
            # Let the tool executor surface this as a tool_error/retry case
            tool_input = {"expression": ""}
        selected_tool = "calculator"

    elif intent == "keyword_extraction":
        selected_tool = "keyword_extraction"
        tool_input = {"text": query, "top_n": 5}

    else:
        # "general" and "unknown" both fall through to the LLM directly;
        # no structured tool is needed.
        selected_tool = None
        tool_input = None

    log_event(state, "router", f"Selected tool='{selected_tool}' with input={tool_input}")

    return {
        "selected_tool": selected_tool,
        "tool_input": tool_input,
    }


def route_after_analysis(state: AgentState) -> str:
    """
    Conditional edge function: returns the NAME of the next node.
    Called by LangGraph, not treated as a state-mutating node itself.
    """
    intent = state["intent"]
    if intent in ("calculator", "keyword_extraction"):
        return "tool_executor"
    return "response_generator"


def route_after_tool_execution(state: AgentState) -> str:
    """
    Conditional edge after tool execution: decides whether to retry the
    same tool, give up and go to response generation, or proceed normally.
    """
    if state.get("tool_error") and state["retry_count"] < state["max_retries"]:
        return "tool_executor"  # retry loop
    return "response_generator"
