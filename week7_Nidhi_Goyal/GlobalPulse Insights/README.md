# 🌍 GlobalPulse Insights AI

**Public Health Policy & SDG QA Engine**

GlobalPulse Insights AI is an intelligent, production-grade Retrieval-Augmented Generation (RAG) system engineered to parse macro-level epidemiological and healthcare statistical reports from the World Health Organization (WHO). Built entirely using localized components, the system securely chunks, embeds, indexes, and queries heavy PDF datasets while enforcing iron-clad context alignment and medical training overrides.

---

## 🏗️ System Architecture

The application pipeline is built on an isolated modular design:

1. **Ingestion (`ingestion.py`):** Automatically scans the target local repository storage (`./health_vault`), dynamically handles PDF streaming, parses textual arrays using `PyPDFLoader`, and packages raw streams into LangChain Document layers.
2. **Chunking (`chunking.py`):** Implements a `RecursiveCharacterTextSplitter` configured with a strict context-preserving layout (800 tokens chunk size with a 150 token mathematical sliding overlap matrix) to protect numerical relationships across tables and paragraphs.
3. **Vector Vectorization (`vector_store.py`):** Utilizes `sentence-transformers/all-MiniLM-L6-v2` to vectorize text strings into dense 384-dimensional spatial coordinates, indexing them into an on-disk instance of a `Chroma` database storage layer.
4. **LCEL Reasoning Chain (`app.py`):** Assembles a unified LangChain Expression Language (LCEL) runtime execution sequence linked to a locally hosted **Phi-3 (3.8B)** model via Ollama. It wraps structural guardrails and medical override triggers around the query parameters.
5. **Dashboard Layer (`ui.py`):** Creates an elegant, session-persistent chat interface using Streamlit to track interactive conversations, capture system fallback signals, and format cited source references.

---

## 🛠️ Project File Layout

```text
week7_Nidhi_Goyal/
└── GlobalPulse Insights/
    ├── .gitignore              # Protects environment configurations & DB caches from tracking
    ├── app.py                  # Core LCEL execution engine & Phi-3 LLM integration
    ├── chunking.py             # Sliding character splitter for text continuity
    ├── ingestion.py            # Local vault streaming processor for PDF files
    ├── ui.py                   # Streamlit interactive web dashboard layer
    ├── vector_store.py         # Coordinates disk indexing & persistence via ChromaDB
    └── health_vault/           # Secure folder storage holding raw WHO PDF data

```

---

## ⚡ Technical Setup & Run Guide

### 1. Environment & Dependencies
Initialize a clean local Python environment and install the required LangChain framework components:

```
# Navigate to project root
cd "GlobalPulse Insights"

# Create and trigger virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required frameworks
pip install streamlit langchain langchain-community langchain-ollama langchain-huggingface chromadb pypdf sentence-transformers
```
### 2. Prepare Data & Database Matrix
Place your official WHO PDF documents inside the ./health_vault/ directory, then execute the indexing engine to establish your mathematical coordinate vector database:

```
python vector_store.py
```
### 3. Launch the Application Interface
Spin up the local serving endpoint to interact with the application:

```
streamlit run ui.py
```

---

## 🔒 Implemented Safety Features & Guardrails

- **Anti-Hallucination Fallback**: The core system prompt forces a binary evaluation loop. If relevant context data is missing from the underlying vector database search yield, the system returns a fixed UNKNOWN flag string.

- **Training Bias Override**: The pipeline injects custom explicit directives to force the underlying small language model to suppress internal conversational and medical pre-training weight sets, forcing it to behave strictly as an objective text extractor.

- **Automated File Ignorance**: Uses a detailed .gitignore file to ensure multi-gigabyte local virtual environment runtimes (.venv/) and dynamic local lock databases (storage_db/) never leak into upstream public tracking streams.
