# 🧠 SmartQuery Agent

**Live Demo:** [smart-query-agent.streamlit.app](https://smart-query-agent.streamlit.app/)

A single-agent AI system, built with **LangGraph**, that reads a natural language query, figures out what the user actually wants, routes it to the right specialized tool, and returns a structured answer — all while tracking its own execution as a stateful directed graph.

It's designed to show how one agent can *simulate* multi-agent behavior internally: instead of one execution path handling every query the same way, the system analyzes intent first and dynamically decides which "specialist" should handle it.

---

## What this project does

Given a query like:

- `"what is 12 * (3 + 4)"` → detects a **math** intent → routes to the calculator tool → returns `84`
- `"Nidhi is a 21 years old. Nidhi is a Computer Science undergraduate at JECRC university. Nidhi likes to do DSA"` → detects this is **descriptive text**, not a question → routes to the keyword extraction tool → returns key terms
- `"What's the capital of France?"` → detects a **general** query → routes to an LLM (via OpenRouter's free tier) → returns a conversational answer

The system doesn't just run every query through the same path — it **analyzes intent first**, then picks the appropriate handler, executes it, retries automatically on failure, and logs every step for evaluation.

---

## How it works (architecture)

```
START
  │
  ▼
Query Analyzer   → detects intent (calculator / keyword_extraction / general)
  │
  ▼
Router           → selects the matching tool + builds its structured input
  │
  ├── (tool-based intent) ──▶ Tool Executor ──▶ (retry loop on failure)
  │                                │
  │                                ▼
  └── (general intent) ───────▶ Response Generator ──▶ END
```

- **Query Analyzer** — determines what the user wants. Uses fast rule-based detection (regex + heuristics), with an LLM-based classification path available as a more flexible alternative.
- **Router** — picks the tool, builds its structured JSON input.
- **Tool Executor** — runs the selected tool; on failure, retries up to a configurable limit before giving up gracefully.
- **Response Generator** — formats the final answer from tool output, or calls the LLM directly for general/conversational queries.

---

## Tools available

| Tool | What it does |
|---|---|
| **Calculator** | Safely evaluates math expressions (AST-based parsing — no `eval()`, so it can't execute arbitrary code) |
| **Keyword Extractor** | Pulls out the most significant words from a block of text using frequency counting + stopword filtering |

---

## Key features

- Stateful workflow modeled as a directed graph (LangGraph), not a linear script
- Conditional routing based on detected intent
- Automatic retry loop with a configurable retry ceiling
- JSON-schema-style input/output contracts for each tool
- Execution logging (`logs/execution.log`) and evaluation metrics (`logs/metrics.jsonl`) — tracks selected tool, retries, execution time, and task completion per run
- Free LLM integration via OpenRouter for anything outside the tools' scope
- Two interfaces: a CLI and a Streamlit web app

---

## Project structure

```
week8_Nidhi_Goyal/
├── app/
│   ├── state.py              # shared AgentState schema
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
├── streamlit_app.py            # web UI (deployed version)
├── requirements.txt
├── .env.example
└── README.md
```

---

## Tech stack

- **Language:** Python
- **Workflow framework:** LangGraph
- **LLM integration:** LangChain + OpenRouter (free-tier models)
- **Frontend:** Streamlit
- **Data format:** JSON Schema for tool I/O
- **Evaluation:** Python logging + custom metrics tracking

---

## Setup (run it locally)

```bash
git clone https://github.com/nidhi2355/Celebal-Technologies.git
cd Celebal-Technologies/week8_Nidhi_Goyal

python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
# or: source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and add a free API key from [openrouter.ai/keys](https://openrouter.ai/keys) — only needed for general (non-tool) queries; the calculator and keyword extractor work without it.

## Usage

**CLI — single query:**
```bash
python main.py "what is 12 * (3 + 4)"
```

**CLI — interactive mode:**
```bash
python main.py
```

**Web app (locally):**
```bash
streamlit run streamlit_app.py
```

**Or just use the live deployed version:** [smart-query-agent.streamlit.app](https://smart-query-agent.streamlit.app/)

---

## Example queries to try

- `calculate (2+3)*(4+5)` — nested bracket math
- `extract keywords from: LangGraph makes it easy to build stateful, multi-step AI workflows`
- A short bio or descriptive paragraph, with no explicit "extract keywords" wording
- `What's the capital of France?` — general/conversational

---

## Learning outcomes demonstrated

- Stateful directed graph workflows
- Nodes and conditional edges in agent pipelines
- Tool calling with JSON-schema I/O contracts
- Retry loops and error handling
- Trajectory evaluation via execution logs and metrics

---

## Future enhancements

- Replace rule-based intent detection entirely with LLM-based classification
- Add more tools (web search, document retrieval, RAG-based Q&A)
- Support parallel tool execution for independent sub-tasks
- Persistent, structured evaluation dashboard instead of raw log files

---

## Author

**Nidhi Goyal** — submitted as part of Week 8, Celebal Technologies internship.
