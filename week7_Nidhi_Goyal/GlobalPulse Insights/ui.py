# ui.py
import streamlit as st

# 1. Updated import to match the new function name in app.py
from app import initialize_rag

# Configure the web page
st.set_page_config(page_title="GlobalPulse AI", page_icon="🌍", layout="centered")

st.title("🌍 GlobalPulse Insights AI")
st.markdown("**Public Health Policy & SDG QA Engine**")
st.divider()

# Initialize the RAG engine only once and store it in session state
if "engine" not in st.session_state:
    with st.spinner("Initializing AI Engine and loading WHO datasets... This may take a moment."):
        # 2. Call the newly named function
        st.session_state.engine = initialize_rag()
    st.success("Engine Ready!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question about global health statistics..."):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and display assistant response
    # Generate and display assistant response
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching database and generating response..."):
            
            # Fetch the raw answer from the LLM
            raw_answer = st.session_state.engine.invoke(prompt)
            
            # Intercept the trigger word to enforce the guardrail
            if "UNKNOWN" in raw_answer.upper():
                final_answer = "This answer is not in the context of the knowledge base of this chat bot."
                st.markdown(final_answer)
            else:
                # If it's a real answer, display it with the footnote
                st.markdown(raw_answer)
                st.caption("Note: Based on data up to 2024. For the latest figures, please refer to the WHO website.")

                
                
    # Save assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": final_answer if "UNKNOWN" in raw_answer.upper() else raw_answer})
