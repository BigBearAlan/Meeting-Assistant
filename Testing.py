import streamlit as st
import pandas as pd
from datetime import datetime
import os

# ---------------------------
# Save responses to CSV
# ---------------------------

def save_response(data):

    file_path = "responses.csv"
    df = pd.DataFrame([data])

    if os.path.exists(file_path):
        df.to_csv(file_path, mode="a", header=False, index=False)
    else:
        df.to_csv(file_path, index=False)


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

    promotion_question = "How are you already operating at the next level? 面试问题：你在哪些方面已经在承担更高一级的职责？- 请模拟面试环境快速回答"

    st.write(f"**Question:** {promotion_question}")

    answer = st.text_area("Your Answer", height=200)

    if st.button("Analyze Response"):

        if not answer:
            st.warning("Please write your answer first.")
            st.stop()

        st.session_state.answer = answer

        with st.spinner("Analyzing..."):

            # MOCK ANALYSIS
            result = """
Covered Signals
• Influence — mentioned helping teammates and mentoring.

Missing Signals
• Impact — no measurable outcomes mentioned.
• Scope — no example of larger initiative ownership.

Evidence you could reference
• Led checkout optimization project that increased conversion by 14%.
• Coordinated cross-team redesign across 3 teams.
"""

        st.session_state.analysis_result = result


# ---------------------------
# Show Analysis + Feedback
# ---------------------------

if st.session_state.analysis_result:

    st.subheader("Analysis")
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


if os.path.exists("responses.csv"):
    df = pd.read_csv("responses.csv")

    st.subheader("Collected Responses")

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Responses CSV",
        csv,
        "responses.csv",
        "text/csv",
        key="download-csv"
    )
