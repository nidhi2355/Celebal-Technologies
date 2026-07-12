"""
Tool Executor node.

Runs the tool selected by the router. On failure, increments retry_count
and clears the error state ready for another pass through the loop; the
route_after_tool_execution conditional edge decides whether that retry
actually happens, or whether we cut our losses and move on.
"""

from app.state import AgentState
from app.tools import TOOL_REGISTRY
from app.logger import log_event


def execute_tool(state: AgentState) -> AgentState:
    tool_name = state.get("selected_tool")
    tool_input = state.get("tool_input") or {}
    retry_count = state.get("retry_count", 0)

    tool_fn = TOOL_REGISTRY.get(tool_name)

    if tool_fn is None:
        log_event(state, "tool_executor", f"No tool registered for '{tool_name}'")
        return {
            "tool_error": f"Unknown tool: {tool_name}",
            "retry_count": retry_count + 1,
        }

    try:
        result = tool_fn(tool_input)
        log_event(state, "tool_executor", f"Tool '{tool_name}' succeeded: {result}")
        return {
            "tool_output": result,
            "tool_error": None,
        }
    except Exception as e:
        log_event(
            state,
            "tool_executor",
            f"Tool '{tool_name}' failed on attempt {retry_count + 1}: {e}",
        )
        return {
            "tool_error": str(e),
            "retry_count": retry_count + 1,
        }
