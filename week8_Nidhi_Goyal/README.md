# SmartQuery Agent

A lightweight, single-agent system built with **LangGraph** that demonstrates
stateful agentic AI: query analysis, conditional routing, tool execution with
retries, and response generation — all as a directed graph.

## How it works

```
START
  |
  v
query_analyzer   -> detects intent: calculator / keyword_extraction / general
  |
  v
router           -> selects tool + builds structured tool_input
  |
  +-- conditional --+
  |                  |
  v                  v
tool_executor    response_generator
  | ^                  ^
  | | (retry loop)     |
  +-+------------------+
                        v
                       END
```

- **Calculator tool** — safely evaluates arithmetic expressions (AST-based, no `eval`).
- **Keyword extraction tool** — frequency + stopword-based keyword pulling.
- **General queries** — routed to an LLM via OpenRouter (free-tier models).
- **Retry loop** — failed tool calls retry up to `max_retries` before falling back gracefully.
- **Logging & metrics** — every run appends a trace to `logs/execution.log` and a
  JSON summary line to `logs/metrics.jsonl` (tool selected, retries, execution time, completion).

## Project structure

```
smartquery_agent/
├── app/
│   ├── state.py              # AgentState schema
│   ├── llm.py                 # OpenRouter LLM client
│   ├── logger.py              # execution logging + metrics
│   ├── graph.py                # LangGraph StateGraph assembly
│   ├── tools/
│   │   ├── calculator.py
│   │   └── keyword_extractor.py
│   └── nodes/
│       ├── query_analyzer.py
│       ├── router.py
│       ├── tool_executor.py
│       └── response_generator.py
├── main.py                     # CLI entry point
├── streamlit_app.py            # optional web UI
├── requirements.txt
└── .env.example
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your free OpenRouter API key from https://openrouter.ai/keys
```

## Usage

**CLI, single query:**
```bash
python main.py "what is 12 * (3 + 4)"
```

**CLI, interactive mode:**
```bash
python main.py
```

**Web UI:**
```bash
streamlit run streamlit_app.py
```

## Example queries to try

- `"calculate 45 * 3 - 10"` → routed to calculator tool
- `"extract keywords from: LangGraph makes it easy to build stateful, multi-step AI workflows"` → routed to keyword extraction tool
- `"what's the capital of France?"` → routed to the LLM (general intent)

## Extending it (per the project's roadmap)

- Add a new tool: write a `run(tool_input) -> dict` function + schema in `app/tools/`,
  register it in `app/tools/__init__.py`'s `TOOL_REGISTRY`, and add a detection rule
  in `app/nodes/query_analyzer.py`.
- Swap rule-based intent detection for LLM-based classification: replace the body
  of `analyze_query()` in `app/nodes/query_analyzer.py` — the function signature
  stays the same.
- Parallel tool execution: LangGraph supports fan-out/fan-in via multiple edges
  from one node; independent tools can run as sibling nodes merged before
  `response_generator`.
- RAG: add a `retriever` tool following the same `run(tool_input) -> dict` pattern.
