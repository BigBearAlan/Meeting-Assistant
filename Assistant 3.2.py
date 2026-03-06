import streamlit as st
import sounddevice as sd
import scipy.io.wavfile as wav
import subprocess
import tempfile
import numpy as np
import re
import time
from openai import OpenAI

# -----------------------------
# Streamlit setup
# -----------------------------

st.set_page_config(page_title="AI Meeting Assistant", layout="wide")
st.title("AI Meeting Assistant")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# -----------------------------
# Audio settings
# -----------------------------

SAMPLE_RATE = 16000
DURATION = 4  # seconds per audio chunk

WHISPER_MODEL = "./whisper.cpp/models/ggml-base.en.bin"
WHISPER_BINARY = "./whisper.cpp/build/bin/whisper-cli"

# -----------------------------
# Question detection rules
# -----------------------------

QUESTION_STARTERS = [
    "what","why","how","when","where","which","who",
    "tell me","can you","could you","would you",
    "walk me through","describe","explain"
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


# -----------------------------
# Whisper transcription
# -----------------------------

def record_audio():

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    return audio


def transcribe_audio(audio):

    with tempfile.NamedTemporaryFile(suffix=".wav") as temp:

        wav.write(temp.name, SAMPLE_RATE, audio)

        cmd = [
            WHISPER_BINARY,
            "-m", WHISPER_MODEL,
            "-f", temp.name,
            "-nt"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        return result.stdout.strip()


# -----------------------------
# OpenAI suggestion generation
# -----------------------------

def generate_suggestion(question, user_goal, evidence):

    prompt = f"""
You are a real-time meeting assistant.

Return ONE short suggestion (max 20 words) to help the user answer well.

User goal:
{user_goal}

Evidence:
{evidence}

Interviewer question:
{question}

Output format:
Suggestion: <one sentence>
"""

    resp = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return resp.output_text.strip()


# -----------------------------
# UI Inputs
# -----------------------------

st.subheader("User Context")

user_goal = st.text_input(
    "User Goal",
    value="Perform well in an interview and demonstrate impact"
)

evidence = st.text_area(
    "Evidence",
    value="- Led 8 engineers\n- Reduced delivery time 35%\n- Improved reliability to 99.95%"
)

start_button = st.button("Start Listening")


# -----------------------------
# Session state
# -----------------------------

if "suggestion" not in st.session_state:
    st.session_state.suggestion = ""

if "transcript" not in st.session_state:
    st.session_state.transcript = ""


# -----------------------------
# Main listening loop
# -----------------------------

if start_button:

    st.success("Listening...")

    transcript_placeholder = st.empty()
    suggestion_placeholder = st.empty()

    while True:

        audio = record_audio()

        transcript = transcribe_audio(audio)

        if transcript:

            st.session_state.transcript = transcript

            transcript_placeholder.write(
                f"Transcript: {transcript}"
            )

            if detect_question(transcript):

                start_time = time.time()

                suggestion = generate_suggestion(
                    transcript,
                    user_goal,
                    evidence
                )

                latency = round(time.time() - start_time, 2)

                st.session_state.suggestion = suggestion

                suggestion_placeholder.write(
                    f"Suggestion: {suggestion}"
                )

                suggestion_placeholder.caption(
                    f"Latency: {latency}s"
                )
