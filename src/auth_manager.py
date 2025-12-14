import streamlit as st

def show_token_creation_steps():
    st.markdown("""
    ### 🔧 How to Create a Confluence API Token
    1. Open [this link](https://id.atlassian.com/manage-profile/security/api-tokens)
    2. Click **Create API token**
    3. Give it a label (e.g., `chatbot-access`)
    4. Click **Create**
    5. Copy the generated token
    6. Paste it into your Streamlit secrets config
    """)

def get_credentials():
    """
    Returns (email, token) from Streamlit secrets.
    If missing, shows instructions and stops execution.
    """
    email = st.secrets.get("CONFLUENCE_EMAIL")
    token = st.secrets.get("CONFLUENCE_API_TOKEN")

    if email and token:
        return email, token

    st.error("❌ Confluence credentials not found in secrets.")
    show_token_creation_steps()
    st.stop()  # Prevents app from continuing

def reset_credentials():
    """
    Placeholder for local dev only — not usable on Streamlit Cloud.
    """
    st.warning("⚠️ Credential reset is not supported on Streamlit Cloud. Please update secrets manually.")