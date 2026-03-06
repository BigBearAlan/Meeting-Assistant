import os
import re
import time
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Question → Suggestion MVP", layout="wide")
st.title("Question → Suggestion MVP")

TRANSCRIPT_FILE = "transcript.txt"

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

QUESTION_STARTERS = [
    "what", "why", "how", "when", "where", "which", "who",
    "tell me", "can you", "could you", "would you",
    "walk me through", "describe", "explain"
]

def detect_question(text: str) -> bool:
    t = (text or "").strip().lower()

    if not t:
        return False

    if "?" in t:
        return True

    for starter in QUESTION_STARTERS:
        if t.startswith(starter + " ") or t == starter:
            return True

    pattern = r"^\s*(what|why|how|when|where|which|who|tell me|can you|could you|would you|walk me through|describe|explain)\b"
    return re.search(pattern, t) is not None


def generate_suggestion(question: str, user_goal: str, evidence: str) -> str:
    prompt = f"""
You are a real-time meeting assistant.
Return ONE short suggestion (max 20 words) to help the user answer well.

User goal:
{user_goal}

Evidence (facts the user can cite):
{evidence}

Interviewer question:
{question}

Output format:
Suggestion: <one sentence>
""".strip()

    resp = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return resp.output_text.strip()


def read_latest_line():
    if not os.path.exists(TRANSCRIPT_FILE):
        return ""

    with open(TRANSCRIPT_FILE, "r") as f:
        lines = f.read().splitlines()

    if not lines:
        return ""

    return lines[-1]


st.subheader("User Context")

user_goal = st.text_input(
    "User goal",
    value="Perform well in an interview and demonstrate impact."
)

evidence = st.text_area(
    "Evidence",
    height=140,
    value="- Led 8 engineers\n- Reduced delivery time 35%\n- Improved reliability to 99.95% uptime"
)

if "last_processed" not in st.session_state:
    st.session_state.last_processed = ""

if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""

st.subheader("Live Transcript")

latest_line = read_latest_line()

st.write(latest_line if latest_line else "Waiting for transcript...")

if latest_line and latest_line != st.session_state.last_processed:

    st.session_state.last_processed = latest_line

    if detect_question(latest_line):

        start = time.time()

        suggestion = generate_suggestion(latest_line, user_goal, evidence)

        latency = round(time.time() - start, 2)

        st.session_state.suggestion = suggestion
        st.session_state.latency = latency


st.subheader("Suggestion")

if st.session_state.suggestion:
    st.write(st.session_state.suggestion)
    st.caption(f"Latency: {st.session_state.latency}s")
else:
    st.write("No suggestion yet.")


time.sleep(2)
st.rerun()
