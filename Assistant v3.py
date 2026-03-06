import streamlit as st
import pandas as pd
from datetime import datetime
import os
from openai import OpenAI
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
You are an experienced promotion interview strategist helping a candidate strengthen their answer.

Your task is to identify what signals the answer actually sends to a promotion panel and suggest what stronger signals could be added.

Language rule:
Respond in the same language used in the user's answer.

If the answer is Chinese → respond in Chinese.  
If the answer is English → respond in English.

Response style:
• Concise  
• Bullet points only  
• One short sentence per bullet  
• Avoid long explanations

Evaluation lenses (not strict rules):
Promotion panels usually look for signals such as:
- Impact — measurable results or business outcomes
- Scope — ownership of larger initiatives or broader responsibility
- Influence — leading people, aligning stakeholders, driving decisions
- Next-level behavior — already acting at the next level
- Strategic thinking — connecting work to larger business goals
- Ownership — initiating and driving work without being asked

Do NOT force all lenses.  
Focus only on the signals that actually matter for this answer.

Evaluation signals should adapt to the Target Role.

Do NOT assume corporate promotion signals.

First infer what signals interviewers for this role would care about.

Inputs:

Target Role:
{st.session_state.target_role}

Promotion Question:
{promotion_question}

User Evidence Document:
{st.session_state.evidence_doc}

User Answer:
{answer}

Tasks:

Step 0 — Check alignment between Target Role and Evidence. - If the evidence comes from a different field,
suggest ways the candidate could reposition the experience.

Step 1 — Identify the strongest signals already present in the answer (max 3)

Step 2 — Identify the most important missing signals that would make a promotion panel more confident.

Step 3 — Suggest specific examples or achievements from the evidence document that could strengthen the answer.

Focus on practical additions the candidate could say.

Output format:

Signals already shown
- ...

Missing signals that would strengthen the answer
- ...

Evidence the user could add
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
        

        
        data = {
            "timestamp": datetime.now(),
            "target_role": st.session_state.get("target_role"),
            "evidence_doc": st.session_state.get("evidence_doc"),
            "question": promotion_question,
            "answer": st.session_state.get("answer"),
            "analysis": result,
            "feedback": "not_provided"
        }

        save_response(data)
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


