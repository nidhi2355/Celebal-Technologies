"""
Graph assembly.

Wires the nodes from app/nodes into a LangGraph StateGraph:

    START
      |
      v
  query_analyzer
      |
      v
     router  (select_tool -- a real node, not just an edge function)
      |
      +-- (conditional: route_after_analysis) --+
      |                                          |
      v                                          v
  tool_executor <--(retry loop)--+       response_generator
      |                          |                |
      +--(conditional: route_after_tool_execution)+
                                                   v
                                                  END
"""

from langgraph.graph import StateGraph, START, END
from app.state import AgentState
from app.nodes import (
    analyze_query,
    select_tool,
    route_after_analysis,
    route_after_tool_execution,
    execute_tool,
    generate_response,
)


def build_graph():
    graph = StateGraph(AgentState)

    # --- register nodes ---
    graph.add_node("query_analyzer", analyze_query)
    graph.add_node("router", select_tool)
    graph.add_node("tool_executor", execute_tool)
    graph.add_node("response_generator", generate_response)

    # --- edges ---
    graph.add_edge(START, "query_analyzer")
    graph.add_edge("query_analyzer", "router")

    # Conditional branch: tool-based intents go to tool_executor,
    # everything else skips straight to response_generator.
    graph.add_conditional_edges(
        "router",
        route_after_analysis,
        {
            "tool_executor": "tool_executor",
            "response_generator": "response_generator",
        },
    )

    # Conditional branch: retry the tool on failure (up to max_retries),
    # otherwise proceed to generate the (possibly error) response.
    graph.add_conditional_edges(
        "tool_executor",
        route_after_tool_execution,
        {
            "tool_executor": "tool_executor",
            "response_generator": "response_generator",
        },
    )

    graph.add_edge("response_generator", END)

    return graph.compile()


# Compiled once at import time so repeated calls (e.g. from Streamlit)
# don't rebuild the graph on every request.
compiled_graph = build_graph()
