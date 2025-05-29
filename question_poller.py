# butterfly_ui.py
# Streamlit UI that polls Livestorm for new questions and displays Q&A powered by Mistral

import os
import tempfile
import requests
import streamlit as st
from dotenv import load_dotenv
from answer_engine import answer_question
from streamlit_autorefresh import st_autorefresh

# --- Load defaults from .env ---
load_dotenv()
def_env_token = os.getenv("LIVESTORM_API_TOKEN", "")
def_env_session = os.getenv("LIVESTORM_SESSION_ID", "")
def_env_mistral = os.getenv("MISTRAL_API_KEY", "")

# --- Streamlit page setup ---
st.set_page_config(page_title="🦋 Butterfly Q&A", layout="wide")
st.title("🦋 Butterfly Livestorm Q&A")

# --- Session state for connection ---
if "connected" not in st.session_state:
    st.session_state.connected = False
if "token" not in st.session_state:
    st.session_state.token = def_env_token
if "session_id" not in st.session_state:
    st.session_state.session_id = def_env_session

# --- Connection inputs ---
if not st.session_state.connected:
    st.subheader("Connect Butterfly")
    st.session_state.token = st.text_input(
        "Livestorm API Token", value=st.session_state.token, type="password"
    )
    st.session_state.session_id = st.text_input(
        "Livestorm Session ID", value=st.session_state.session_id
    )
    if st.button("Connect"):
        with st.spinner("🦋 Connecting Butterfly..."):
            lines = []
            if def_env_mistral:
                lines.append(f"MISTRAL_API_KEY={def_env_mistral}")
            lines.append(f"LIVESTORM_API_TOKEN={st.session_state.token}")
            lines.append(f"LIVESTORM_SESSION_ID={st.session_state.session_id}")
            with open('.env','w') as f:
                f.write("\n".join(lines))
            st.session_state.connected = True
            st.success("🦋 Butterfly connected")
    st.stop()

# --- After connection ---
LIVESTORM_API_TOKEN = st.session_state.token
LIVESTORM_SESSION_ID = st.session_state.session_id
if not LIVESTORM_API_TOKEN or not LIVESTORM_SESSION_ID:
    st.error("Invalid connection settings.")
    st.stop()

# --- Auto-refresh for polling every 6 seconds ---
st_autorefresh = st_autorefresh(interval=6_000, key="poll_timer")

# --- Livestorm API setup ---
API_URL = (
    f"https://api.livestorm.co/v1/sessions/{LIVESTORM_SESSION_ID}"
    "/questions?include=asker&include=responder"
)
HEADERS = {"accept": "application/vnd.api+json", "Authorization": LIVESTORM_API_TOKEN}

# --- PDF upload once ---
if "pdf_path" not in st.session_state:
    doc_file = st.file_uploader("Upload Knowledge PDF", type=["pdf"])
    if doc_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(doc_file.read())
            st.session_state.pdf_path = tmp.name
        st.success(f"📄 Loaded: {doc_file.name}")
    else:
        st.info("Upload your knowledge PDF to get started.")
        st.stop()

# --- Initialize Q&A lists ---
if "seen_ids" not in st.session_state:
    st.session_state.seen_ids = set()
if "qa_pairs" not in st.session_state:
    st.session_state.qa_pairs = []  # list of dicts {id, question, answer}

# --- Poll new questions ---
try:
    resp = requests.get(API_URL, headers=HEADERS)
    resp.raise_for_status()
    for item in resp.json().get("data", []):
        qid = item["id"]
        q_text = item["attributes"]["question"]
        if qid not in st.session_state.seen_ids:
            st.session_state.seen_ids.add(qid)
            st.session_state.qa_pairs.insert(0, {"id": qid, "question": q_text, "answer": None})
except Exception as e:
    st.error(f"Error polling Livestorm: {e}")

# --- Generate answers for unanswered questions ---
for qa in st.session_state.qa_pairs:
    if qa["answer"] is None:
        try:
            qa["answer"] = answer_question(st.session_state.pdf_path, qa["question"])
        except Exception as err:
            qa["answer"] = f"Error: {err}"

# --- Display Q&A cards with loader or answer ---
st.subheader("Questions & Answers")
# Badge HTML for initials
badge_html = (
    '<div style="display:inline-block; width:36px; height:36px; line-height:36px; '
    'background-color:#6C63FF; border-radius:50%; text-align:center; '
    'color:#FFFFFF; font-weight:600; font-size:14px;">FH</div>'
)

for qa in st.session_state.qa_pairs:
    q_text = qa["question"]
    answer_text = qa.get("answer") or "Butterfly thinking..."
    html = (
        f'<div style="background-color:#F8F9FA; padding:16px; border-radius:8px; '
        f'margin-bottom:12px; border:1px solid #E0E0E0;">'
        f'<div style="display:flex; align-items:center;">{badge_html}'
        f'<p style="font-size:16px; font-weight:600; margin:0 0 0 12px; color:#333333;">'
        f'{q_text}</p></div>'
        f'<div style="margin-top:12px; display:flex; align-items:center;">'
        f'<span style="font-size:20px; margin-right:8px; color:#6C63FF;">🦋</span>'
        f'<span style="font-size:15px; color:#333333;">{answer_text}</span></div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)

# --- Requirements ---
# pip install streamlit requests mistralai python-dotenv streamlit-autorefresh
# streamlit run butterfly_ui.py