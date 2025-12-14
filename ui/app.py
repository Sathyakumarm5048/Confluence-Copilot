import streamlit as st
import sys
import os

# Ensure backend modules are discoverable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from main import answer_query, startup

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Confluence Copilot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Confluence Copilot")
st.caption("Your AI assistant for navigating Confluence knowledge.")

# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------
if "initialized" not in st.session_state:
    with st.spinner("Initializing Confluence Copilot..."):
        startup()
    st.session_state.initialized = True

if "messages" not in st.session_state:
    st.session_state.messages = []

if "reset_chat" not in st.session_state:
    st.session_state.reset_chat = False

# ---------------------------------------------------------
# Reset Chat Handling
# ---------------------------------------------------------
if st.session_state.reset_chat:
    st.session_state.messages = []
    st.session_state.reset_chat = False
    st.success("✅ Chat history cleared. Start fresh!")

# ---------------------------------------------------------
# Display Chat History
# ---------------------------------------------------------
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
            try:
                response = answer_query(user_input)
            except Exception as e:
                response = f"❌ Error: {str(e)}"
            st.markdown(response)

    # Save assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

# ---------------------------------------------------------
# Reset Chat Button
# ---------------------------------------------------------
if st.button("Reset Chat"):
    st.session_state.reset_chat = True