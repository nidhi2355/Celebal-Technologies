"""
Response Generator node.

Formats the final answer shown to the user. For tool-based intents it
formats the structured tool_output directly (fast, no LLM call needed).
For "general" queries -- or when a tool exhausted its retries -- it
calls the LLM for a free-form response.
"""

from app.state import AgentState
from app.llm import get_llm
from app.logger import log_event


def generate_response(state: AgentState) -> AgentState:
    intent = state["intent"]
    tool_output = state.get("tool_output")
    tool_error = state.get("tool_error")

    # Case 1: tool succeeded -- format its structured output directly.
    if tool_output and not tool_error:
        if intent == "calculator":
            response = f"The result of `{tool_output['expression']}` is **{tool_output['result']}**."
        elif intent == "keyword_extraction":
            keywords = ", ".join(tool_output["keywords"]) or "(no significant keywords found)"
            response = f"Top keywords: {keywords}"
        else:
            response = str(tool_output)
        task_completed = True

    # Case 2: tool was selected but ultimately failed after retries.
    elif intent in ("calculator", "keyword_extraction") and tool_error:
        response = (
            f"I tried to handle this with the {intent} tool but ran into an error "
            f"after {state.get('retry_count', 0)} attempt(s): {tool_error}"
        )
        task_completed = False

    # Case 3: general query -- defer to the LLM.
    else:
        try:
            llm = get_llm()
            reply = llm.invoke(state["query"])
            response = reply.content
            task_completed = True
        except Exception as e:
            response = f"I couldn't generate a response: {e}"
            task_completed = False

    log_event(state, "response_generator", f"Final response prepared (completed={task_completed})")

    import time
    return {
        "response": response,
        "task_completed": task_completed,
        "end_time": time.time(),
    }
