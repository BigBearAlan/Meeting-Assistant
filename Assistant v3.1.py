import os
import re
import time
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Question → Suggestion MVP", layout="wide")
st.title("Question → Suggestion MVP")

# 1) OpenAI client
# Set OPENAI_API_KEY in your environment
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 2) Rule-based question detection
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

    # Check for common question starters near the start of the line/sentence
    for starter in QUESTION_STARTERS:
        if t.startswith(starter + " " ) or t == starter:
            return True

    # Regex fallback: question word near beginning
    pattern = r"^\s*(what|why|how|when|where|which|who|tell me|can you|could you|would you|walk me through|describe|explain)\b"
    return re.search(pattern, t) is not None

# 3) Ask AI for a single suggestion
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
        model="gpt-5-mini",
        input=prompt
    )
    return resp.output_text.strip()

# UI inputs
st.subheader("Inputs")
user_goal = st.text_input("User goal (one line)", value="Perform well in an interview and demonstrate impact.")
evidence = st.text_area("Evidence (bullet points; metrics; wins)", height=140,
                        value="- Led 8 engineers\n- Reduced delivery time 35%\n- Improved reliability to 99.95% uptime")

transcript_chunk = st.text_area("Paste latest transcript chunk here", height=220,
                                placeholder="Interviewer: Tell me about a time you led a difficult project.")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Detect question"):
        is_q = detect_question(transcript_chunk)
        st.session_state["is_question"] = is_q
        st.success("Question detected.") if is_q else st.info("No question detected.")

with col2:
    if st.button("Generate suggestion (if question)"):
        is_q = detect_question(transcript_chunk)
        st.session_state["is_question"] = is_q

        if not is_q:
            st.warning("No question detected. Paste a question or include '?' / question starter.")
        else:
            start = time.time()
            suggestion = generate_suggestion(transcript_chunk, user_goal, evidence)
            latency = round(time.time() - start, 2)
            st.session_state["suggestion"] = suggestion
            st.session_state["latency"] = latency

# Output
st.subheader("Output")
if st.session_state.get("suggestion"):
    st.write(st.session_state["suggestion"])
    st.caption(f"Latency: {st.session_state.get('latency')}s")
else:
    st.write("No suggestion yet.")
