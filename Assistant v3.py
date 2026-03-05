import streamlit as st
import pandas as pd
from datetime import datetime
import os
# from openai import OpenAI
import gspread
from google.oauth2.service_account import Credentials

# ---------------------------
# Initialize OpenAI Client
# ---------------------------

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------------------------
# Google Sheets Setup
# ---------------------------

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

gc = gspread.authorize(creds)

sheet = gc.open("Testing Data").sheet1

# ---------------------------
# Save responses to Google Sheets
# ---------------------------

def save_response(data):

    sheet.append_row([
        str(data["timestamp"]),
        data["target_role"],
        data["evidence_doc"],
        data["question"],
        data["answer"],
        data["analysis"],
        data["feedback"]
    ])

# ---------------------------
# Initialize session state
# ---------------------------

if "step" not in st.session_state:
    st.session_state.step = 1

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "answer" not in st.session_state:
    st.session_state.answer = None

# ---------------------------
# App Title
# ---------------------------

st.title("Promotion Readiness Practice")

# ---------------------------
# STEP 1 — Promotion Context
# ---------------------------

if st.session_state.step == 1:

    st.header("Step 1: Promotion Context")

    target_role = st.text_input("Target Promotion Role (写下想要target的职位)")

    evidence_doc = st.text_area(
        "Evidence Document (Brag Doc / Promotion Packet / Achievements) 写下你的贡献，比如提高30%销售额 etc",
        height=200
    )

    if st.button("Start Practice"):

        if not target_role or not evidence_doc:
            st.warning("Please complete all fields.")
        else:
            st.session_state.target_role = target_role
            st.session_state.evidence_doc = evidence_doc
            st.session_state.step = 2
            st.rerun()

# ---------------------------
# STEP 2 — Promotion Question
# ---------------------------

elif st.session_state.step == 2:

    st.header("Step 2: Promotion Question")

    promotion_question = "How are you already operating at the next level? 面试问题：你在哪些方面已经在承担更高一级的职责？请模拟面试环境快速回答"

    st.write(f"**Question:** {promotion_question}")

    answer = st.text_area("Your Answer", height=200)

    if st.button("Analyze Response"):

        if not answer:
            st.warning("Please write your answer first.")
            st.stop()

        st.session_state.answer = answer

        prompt = f"""
You are evaluating a promotion readiness answer.

Promotion readiness signals:

1. Impact (measurable results)
2. Scope (ownership of large initiatives)
3. Influence (leadership, mentoring, driving decisions)
4. Next-level behavior (already operating at the next level)

Inputs:

Target Role:
{st.session_state.target_role}

Promotion Question:
{promotion_question}

Evidence Document:
{st.session_state.evidence_doc}

User Answer:
{answer}

Tasks:

1. Identify which readiness signals appear in the answer.
2. Identify which signals are missing.
3. Suggest specific evidence from the evidence document that could strengthen the response.
4. Keep the answer concise and practical.

Return output in this format:

Covered Signals
- ...

Missing Signals
- ...

Evidence the user could reference
- ...
"""

        with st.spinner("Analyzing response..."):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert career coach evaluating promotion readiness."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

        result = response.choices[0].message.content
        st.session_state.analysis_result = result

# ---------------------------
# Show Analysis + Feedback
# ---------------------------

if st.session_state.analysis_result:

    st.subheader("AI Analysis")

    st.write(st.session_state.analysis_result)

    feedback = st.radio(
        "Did this surface something you forgot to mention?",
        ["Yes", "No"],
        key="feedback_radio"
    )

    if st.button("Submit Feedback"):

        data = {
            "timestamp": datetime.now(),
            "target_role": st.session_state.get("target_role"),
            "evidence_doc": st.session_state.get("evidence_doc"),
            "question": "How are you already operating at the next level?",
            "answer": st.session_state.get("answer"),
            "analysis": st.session_state.analysis_result,
            "feedback": feedback
        }

        save_response(data)

        st.success("Thanks! Your response has been recorded.")

# ---------------------------
# Restart Button
# ---------------------------

if st.button("Restart Practice"):

    st.session_state.step = 1
    st.session_state.analysis_result = None
    st.session_state.answer = None
    st.rerun()

# ---------------------------
# Show collected data
# ---------------------------

if os.path.exists("responses.csv"):

    st.subheader("Collected Responses")

    df = pd.read_csv("responses.csv")

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download CSV",
        csv,
        "responses.csv",
        "text/csv"
    )
