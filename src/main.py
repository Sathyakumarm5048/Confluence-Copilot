import os
import sys
import logging
from typing import List
import requests
from bs4 import BeautifulSoup
import numpy as np
import base64
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from transformers import pipeline
import transformers
import warnings
import streamlit as st

from auth_manager import get_credentials

# ---------------------------------------------------------
#  Suppress unwanted logs/warnings/progress bars
# ---------------------------------------------------------
warnings.filterwarnings("ignore", category=UserWarning)
transformers.logging.set_verbosity_error()
os.environ["TRANSFORMERS_NO_TQDM"] = "1"

# ---------------------------------------------------------
#  Logging
# ---------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("conf-copilot")

# ---------------------------------------------------------
#  Confluence Configuration
# ---------------------------------------------------------
CONFLUENCE_BASE_URL = st.secrets.get(
    "CONFLUENCE_URL",
    "https://revolution5048.atlassian.net/wiki"
)

DEFAULT_SPACE_KEY = st.secrets.get("CONFLUENCE_SPACE_KEY", "~satspc")

# ---------------------------------------------------------
#  Globals populated at runtime
# ---------------------------------------------------------
email = None
token = None
pages = None
chunks = None
embedder = None
summarizer = None

# ---------------------------------------------------------
#  Authentication
# ---------------------------------------------------------
def get_auth_headers():
    encoded = base64.b64encode(f"{email}:{token}".encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json"
    }

# ---------------------------------------------------------
#  Fetch Confluence Pages
# ---------------------------------------------------------
def fetch_pages(space_key: str = DEFAULT_SPACE_KEY, limit: int = 50) -> dict:
    headers = get_auth_headers()
    url = f"{CONFLUENCE_BASE_URL}/rest/api/content"
    params = {
        "spaceKey": space_key,
        "expand": "body.storage",
        "limit": limit,
        "type": "page"
    }

    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

# ---------------------------------------------------------
#  Preprocessing
# ---------------------------------------------------------
def preprocess_content(page_data: dict) -> List[str]:
    texts = []
    for page in page_data.get("results", []):
        html = page["body"]["storage"]["value"]
        text = BeautifulSoup(html, "html.parser").get_text()
        texts.append(text)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = []
    for text in texts:
        chunks.extend(splitter.split_text(text))

    return chunks

# ---------------------------------------------------------
#  Embedding + Semantic Search
# ---------------------------------------------------------
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def semantic_search(chunks: List[str], query: str) -> List[str]:
    query_emb = embedder.encode(query)
    chunk_embs = [(chunk, embedder.encode(chunk)) for chunk in chunks]

    ranked = sorted(
        chunk_embs,
        key=lambda ce: cosine_similarity(query_emb, ce[1]),
        reverse=True
    )

    return [chunk for chunk, _ in ranked[:3]]

# ---------------------------------------------------------
#  Summarization
# ---------------------------------------------------------
def summarize(chunks: List[str]) -> str:
    try:
        partial_summaries = []
        for chunk in chunks:
            s = summarizer(chunk, max_length=120, min_length=40, do_sample=False)
            clean = s[0]["summary_text"].strip()
            partial_summaries.append(clean)

        combined_text = " ".join(partial_summaries)
        final = summarizer(combined_text, max_length=150, min_length=60, do_sample=False)
        return final[0]["summary_text"].strip()

    except Exception as e:
        logger.error("Summarization failed: %s", e)
        return "Could not generate summary. Showing raw chunks:\n" + "\n".join(chunks)

# ---------------------------------------------------------
#  Intent Detection
# ---------------------------------------------------------
LINK_TRIGGERS = ["link", "url", "page", "reference", "location", "source of"]
CONTENT_TRIGGERS = ["explain", "describe", "summarize", "started", "origin", "details"]

def detect_intent(query: str) -> str:
    q = query.lower()
    if any(trigger in q for trigger in LINK_TRIGGERS):
        if any(trigger in q for trigger in CONTENT_TRIGGERS):
            return "content"
        return "link"
    return "content"

# ---------------------------------------------------------
#  Page Link Lookup
# ---------------------------------------------------------
def get_page_link(page_data: dict, query: str) -> str:
    query_lower = query.lower()
    words = query_lower.split()
    keyword = next((w for w in reversed(words) if w not in LINK_TRIGGERS), None)

    matches = []
    for page in page_data.get("results", []):
        title = page.get("title", "Untitled")

        if "_links" in page and "webui" in page["_links"]:
            url = f"{CONFLUENCE_BASE_URL}{page['_links']['webui']}"
        else:
            url = f"{CONFLUENCE_BASE_URL}/pages/{page.get('id', '')}"

        if keyword and keyword in title.lower():
            matches.append(f"{title}: {url}")

    return "\n".join(matches) if matches else f"No matching page found for '{keyword}'."

# ---------------------------------------------------------
#  Chatbot Response
# ---------------------------------------------------------
def chatbot_response(query: str) -> str:
    if any(v is None for v in [pages, chunks, embedder, summarizer]):
        return "System is still initializing. Please try again shortly."

    intent = detect_intent(query)

    if intent == "link":
        return get_page_link(pages, query)

    try:
        relevant = semantic_search(chunks, query)
        summary = summarize(relevant)
        return summary

    except Exception as e:
        logger.exception("Error inside chatbot_response: %s", e)
        return "An error occurred while processing your query."

def answer_query(query: str) -> str:
    logger.info(f"answer_query received: {query}")
    result = chatbot_response(query)
    logger.info(f"answer_query returned: {repr(result)}")
    return result

# ---------------------------------------------------------
#  Startup (Streamlit-safe)
# ---------------------------------------------------------
def startup():
    global email, token, embedder, summarizer, pages, chunks

    logger.info("STARTUP: entered startup()")

    try:
        email, token = get_credentials()
        logger.info("STARTUP: credentials loaded")
    except Exception as e:
        logger.error("STARTUP FAILED at credentials: %s", e)
        return

    try:
        logger.info("STARTUP: loading embedder...")

        @st.cache_resource
        def load_embedder():
            model_name = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            return SentenceTransformer(model_name, device="cpu", trust_remote_code=True)

        embedder = load_embedder()
        logger.info("STARTUP: embedder loaded")
    except Exception as e:
        logger.error("STARTUP FAILED at embedder: %s", e)
        return

    try:
        logger.info("STARTUP: loading summarizer...")
        summarizer = pipeline(
            "summarization",
            model=os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")
        )
        logger.info("STARTUP: summarizer loaded")
    except Exception as e:
        logger.error("STARTUP FAILED at summarizer: %s", e)
        return

    try:
        logger.info("STARTUP: fetching pages...")
        pages = fetch_pages()
        logger.info("STARTUP: pages fetched")
    except Exception as e:
        logger.error("STARTUP FAILED at fetch_pages: %s", e)
        return

    try:
        logger.info("STARTUP: preprocessing content...")
        chunks = preprocess_content(pages)
        logger.info("STARTUP: preprocessing complete")
    except Exception as e:
        logger.error("STARTUP FAILED at preprocess_content: %s", e)
        return

    logger.info("STARTUP: completed successfully")