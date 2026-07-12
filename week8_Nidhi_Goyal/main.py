"""
CLI entry point for SmartQuery Agent.

Usage:
    python main.py "what is 12 * (3 + 4)"
    python main.py            # interactive mode
"""

import sys
import json
from dotenv import load_dotenv

load_dotenv()

from app.graph import compiled_graph
from app.state import new_state
from app.logger import summarize_run


def run_query(query: str, verbose: bool = True) -> dict:
    state = new_state(query)
    final_state = compiled_graph.invoke(state)
    summary = summarize_run(final_state)

    if verbose:
        print("\n" + "=" * 60)
        print(f"Query:    {final_state['query']}")
        print(f"Intent:   {final_state['intent']} (confidence={final_state['intent_confidence']})")
        print(f"Tool:     {final_state.get('selected_tool')}")
        print(f"Retries:  {final_state.get('retry_count', 0)}")
        print(f"Response: {final_state['response']}")
        print("=" * 60)
        print("Metrics:", json.dumps(summary, indent=2))

    return final_state


def interactive_loop():
    print("SmartQuery Agent -- type 'exit' to quit.\n")
    while True:
        query = input("You: ").strip()
        if query.lower() in ("exit", "quit"):
            break
        if not query:
            continue
        run_query(query)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_query(" ".join(sys.argv[1:]))
    else:
        interactive_loop()
