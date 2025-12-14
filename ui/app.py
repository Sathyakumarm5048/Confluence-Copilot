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

st.markdown("""
<style>
.chat-left .stChatMessage {
    text-align: left;
}

.chat-right .stChatMessage {
    text-align: right;
    background-color: #f0f4ff;
    border-radius: 10px;
    padding: 8px;
    margin-left: auto;
    max-width: 80%;
}
</style>
""", unsafe_allow_html=True)

st.title("🤖 Confluence Copilot")
st.caption("Your AI assistant for navigating Confluence knowledge.")

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "initialized" not in st.session_state:
    with st.spinner("Initializing Confluence Copilot..."):
        startup()
    st.session_state.initialized = True

if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_cleared" not in st.session_state:
    st.session_state.chat_cleared = False

# ---------------------------------------------------------
# Reset Chat Button
# ---------------------------------------------------------
if st.button("Reset Chat"):
    st.session_state.messages = []
    st.session_state.chat_cleared = True

# ---------------------------------------------------------
# Show Confirmation Message
# ---------------------------------------------------------
if st.session_state.chat_cleared:
    st.success("✅ Chat history cleared. Start fresh!")
    st.session_state.chat_cleared = False

# ---------------------------------------------------------
# Display Chat History
# ---------------------------------------------------------
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        with st.chat_message("user"):
            st.markdown(f'<div class="chat-left">{content}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message("assistant"):
            st.markdown(f'<div class="chat-right">{content}</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Chat Input
# ---------------------------------------------------------
user_input = st.chat_input("Ask a question about your Confluence space...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = answer_query(user_input)
            except Exception as e:
                response = f"❌ Error: {str(e)}"
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})