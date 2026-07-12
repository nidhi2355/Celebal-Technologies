"""
Execution logging + evaluation metrics.

Every node calls `log_event(state, node_name, detail)` to append a trace
entry to state["trace"]. At the end of a run, `summarize_run(state)`
turns that trace into the metrics the project description asks for:
selected tool, execution time, retries, and task completion status.
"""

import json
import logging
import os
import time
from datetime import datetime

os.makedirs("logs", exist_ok=True)

logger = logging.getLogger("smartquery_agent")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler("logs/execution.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    )
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)


def log_event(state: dict, node_name: str, detail: str) -> None:
    """Append a trace event to state and write it to the logger."""
    event = {
        "node": node_name,
        "timestamp": time.time(),
        "detail": detail,
    }
    state.setdefault("trace", []).append(event)
    logger.info(f"[{node_name}] {detail}")


def summarize_run(state: dict) -> dict:
    """
    Builds the final evaluation summary for a completed run.
    This is what gets logged/printed as the "trajectory evaluation".
    """
    duration = round(state.get("end_time", 0) - state.get("start_time", 0), 4)

    summary = {
        "query": state.get("query"),
        "detected_intent": state.get("intent"),
        "intent_confidence": state.get("intent_confidence"),
        "selected_tool": state.get("selected_tool"),
        "retry_count": state.get("retry_count"),
        "task_completed": state.get("task_completed"),
        "execution_time_seconds": duration,
        "trace_length": len(state.get("trace", [])),
        "timestamp": datetime.utcnow().isoformat(),
    }

    logger.info("RUN SUMMARY: " + json.dumps(summary))

    with open("logs/metrics.jsonl", "a") as f:
        f.write(json.dumps(summary) + "\n")

    return summary
