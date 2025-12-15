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
    
    padding: 20px;
    border-radius: 12px;
    margin-top: 20px;
}
.user-msg, .assistant-msg {
    display: flex;
    margin: 8px 0;
}
.user-msg > div {
    background-color: #ffa500; /* Orange for user prompt */
    color: #000;
    padding: 10px 14px;
    border-radius: 10px;
    max-width: 80%;
    text-align: left;
}
.assistant-msg {
    justify-content: flex-end;
}
.assistant-msg > div {
    background-color: #ff4d4d; /* Red for assistant response */
    color: #fff; /* White text for contrast */
    padding: 10px 14px;
    border-radius: 10px;
    max-width: 80%;
    text-align: left;
}
.speaker-label-left, .speaker-label-right {
    font-weight: bold;
    font-size: 0.9rem;
    margin-bottom: 4px;
    color: #ccc;
}
.speaker-label-left { text-align: left; }
.speaker-label-right { text-align: right; }
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

# Clean empty messages
st.session_state.messages = [
    m for m in st.session_state.messages
    if m.get("content") and str(m.get("content")).strip()
]

# ---------------------------------------------------------
# Reset Chat
# ---------------------------------------------------------
if st.button("Reset Chat"):
    st.session_state.messages = []
    st.success("✅ Chat history cleared. Start fresh!")
    st.rerun()

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

    elif role == "assistant":
        st.markdown('<div class="speaker-label-right">Confluence Copilot:</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="assistant-msg"><div>{content}</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# Chat Input
# ---------------------------------------------------------
user_input = st.chat_input("Ask a question about your Confluence space...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Save temporary assistant placeholder
    st.session_state.messages.append({"role": "assistant", "content": "Thinking..."})
    st.rerun()

# ---------------------------------------------------------
# Replace "Thinking..." with actual response
# ---------------------------------------------------------
if st.session_state.messages:
    last_msg = st.session_state.messages[-1]
    second_last = st.session_state.messages[-2] if len(st.session_state.messages) >= 2 else {}

    if last_msg.get("role") == "assistant" and last_msg.get("content") == "Thinking..." and second_last.get("role") == "user":
        query = second_last.get("content")
        try:
            with st.spinner("Confluence Copilot is thinking..."):
                response = answer_query(query)
        except Exception as e:
            response = f"❌ Error: {str(e)}"
            st.error(f"Details: {str(e)}")

        # Replace placeholder with actual response
        if response and isinstance(response, str) and response.strip() and response != "None":
            st.session_state.messages[-1]["content"] = response
        else:
            st.session_state.messages[-1]["content"] = "⚠️ No response generated. Please try again."

        st.rerun()