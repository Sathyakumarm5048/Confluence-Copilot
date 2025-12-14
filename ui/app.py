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

# ---------------------------------------------------------
# Custom Chat Bubble Styles
# ---------------------------------------------------------
st.markdown("""
<style>
.chat-container {
    background-color: #1e1e1e;
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
}

/* User message bubble */
.user-msg {
    display: flex;
    margin: 8px 0;
}
.user-msg > div {
    background-color: #f7f7f7;
    color: #000;
    padding: 10px 14px;
    border-radius: 10px;
    max-width: 80%;
    text-align: left;
}

/* Assistant message bubble */
.assistant-msg {
    display: flex;
    justify-content: flex-end;
    margin: 8px 0;
}
.assistant-msg > div {
    background-color: #dbeafe;
    color: #000;
    padding: 10px 14px;
    border-radius: 10px;
    max-width: 80%;
    text-align: left;
}

/* Speaker labels */
.speaker-label-left {
    font-weight: bold;
    font-size: 0.9rem;
    margin-bottom: 4px;
    color: #ccc;
    text-align: left;
}
.speaker-label-right {
    font-weight: bold;
    font-size: 0.9rem;
    margin-bottom: 4px;
    color: #ccc;
    text-align: right;
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
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]

    if role == "user":
        st.markdown('<div class="speaker-label-left">You:</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="user-msg"><div>{content}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="speaker-label-right">Confluence Copilot:</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="assistant-msg"><div>{content}</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Chat Input
# ---------------------------------------------------------
user_input = st.chat_input("Ask a question about your Confluence space...")

if user_input:
    # Save and render user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown('<div class="speaker-label-left">You:</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-msg"><div>{user_input}</div></div>', unsafe_allow_html=True)

    # Generate assistant response
    response = None
    try:
        with st.spinner("Thinking..."):
            response = answer_query(user_input)
    except Exception as e:
        response = f"❌ Error: {str(e)}"
        st.error(f"Details: {str(e)}")

    # Only render assistant message if response is valid
    if response and response.strip():
        st.markdown('<div class="speaker-label-right">Confluence Copilot:</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="assistant-msg"><div>{response}</div></div>', unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.warning("⚠️ No response generated. Please try again.")