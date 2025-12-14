import streamlit as st
import sys
import os
import signal

def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)

# Make sure Python can find your backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from main import answer_query, startup

st.set_page_config(
    page_title="Confluence Copilot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Confluence Copilot")
st.caption("Your AI assistant for navigating Confluence knowledge.")

# ---------------------------------------------------------
# Initialize backend once
# ---------------------------------------------------------
if "initialized" not in st.session_state:
    with st.spinner("Initializing Confluence Copilot..."):
        startup()
    st.session_state.initialized = True

# ---------------------------------------------------------
# Chat History
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------
# Chat Input
# ---------------------------------------------------------
user_input = st.chat_input("Ask a question about your Confluence space...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = answer_query(user_input)
            st.markdown(response)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

if st.button("Close Chat"):
    st.write("Shutting down Confluence Copilot...")
    shutdown()