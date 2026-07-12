"""
Optional Streamlit frontend for SmartQuery Agent.

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

import os, streamlit as st
if "OPENROUTER_API_KEY" in st.secrets:
    os.environ["OPENROUTER_API_KEY"] = st.secrets["OPENROUTER_API_KEY"]

from app.graph import compiled_graph
from app.state import new_state
from app.logger import summarize_run


st.set_page_config(page_title="SmartQuery Agent", page_icon="🧠")
st.title("🧠 SmartQuery Agent")
st.caption("Single-agent pipeline with intelligent tool routing (LangGraph)")

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input("Ask something (math, keyword extraction, or general):", "")

if st.button("Run") and query.strip():
    with st.spinner("Routing and executing..."):
        state = new_state(query)
        final_state = compiled_graph.invoke(state)
        summary = summarize_run(final_state)
        st.session_state.history.append((final_state, summary))

for final_state, summary in reversed(st.session_state.history):
    st.markdown("---")
    st.markdown(f"**Query:** {final_state['query']}")
    st.markdown(f"**Response:** {final_state['response']}")

    with st.expander("Execution details"):
        st.write(f"Intent: `{final_state['intent']}` (confidence: {final_state['intent_confidence']})")
        st.write(f"Selected tool: `{final_state.get('selected_tool')}`")
        st.write(f"Retries: {final_state.get('retry_count', 0)}")
        st.write(f"Task completed: {final_state.get('task_completed')}")
        st.json(summary)

    with st.expander("Full trace"):
        st.json(final_state.get("trace", []))
