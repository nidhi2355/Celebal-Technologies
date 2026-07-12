"""
LLM client setup.

Uses LangChain's ChatOpenAI class pointed at OpenRouter's API, which is
OpenAI-compatible. OpenRouter's free-tier models (e.g. models with a
":free" suffix) are used to keep the project cost-free, per the
project's tech stack.

Requires an OPENROUTER_API_KEY environment variable. Get one free at
https://openrouter.ai/keys
"""

import os
from langchain_openai import ChatOpenAI


DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")


def get_llm(temperature: float = 0.2, model: str = None) -> ChatOpenAI:
    """
    Returns a configured ChatOpenAI instance wired to OpenRouter.

    Raises RuntimeError early (with a clear message) if the API key is
    missing, rather than failing deep inside a graph node.
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Copy .env.example to .env and "
            "add your key from https://openrouter.ai/keys"
        )

    return ChatOpenAI(
        model=model or DEFAULT_MODEL,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=temperature,
        default_headers={
            # OpenRouter uses these optional headers for its public leaderboard
            "HTTP-Referer": "https://github.com/your-username/smartquery-agent",
            "X-Title": "SmartQuery Agent",
        },
    )
