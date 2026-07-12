"""
AgentState: the single object that flows through every node in the graph.

LangGraph passes this dict-like object from node to node. Each node reads
the fields it needs and returns a partial update that gets merged into it.
"""

from typing import TypedDict, Optional, Literal, List
import time


IntentType = Literal["calculator", "keyword_extraction", "general", "unknown"]


class AgentState(TypedDict, total=False):
    # --- input ---
    query: str                      # raw user query

    # --- query analysis ---
    intent: IntentType              # detected intent
    intent_confidence: float        # 0.0 - 1.0, how sure the analyzer is

    # --- routing / execution ---
    selected_tool: Optional[str]    # name of the tool chosen by the router
    tool_input: Optional[dict]      # structured input passed to the tool
    tool_output: Optional[str]      # raw result returned by the tool
    tool_error: Optional[str]       # error message if the tool call failed

    # --- retry handling ---
    retry_count: int                # how many times we've retried this step
    max_retries: int                # ceiling before we give up gracefully

    # --- final output ---
    response: Optional[str]         # final formatted answer shown to the user

    # --- execution trace / evaluation ---
    start_time: float
    end_time: float
    task_completed: bool
    trace: List[dict]               # list of {node, timestamp, detail} events


def new_state(query: str, max_retries: int = 2) -> AgentState:
    """Factory for a fresh AgentState at the start of a run."""
    return AgentState(
        query=query,
        intent="unknown",
        intent_confidence=0.0,
        selected_tool=None,
        tool_input=None,
        tool_output=None,
        tool_error=None,
        retry_count=0,
        max_retries=max_retries,
        response=None,
        start_time=time.time(),
        end_time=0.0,
        task_completed=False,
        trace=[],
    )
