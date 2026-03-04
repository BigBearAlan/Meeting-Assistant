import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Promotion Readiness Practice")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1

# ----------------------
# STEP 1: Collect context
# ----------------------

if st.session_state.step == 1:

    st.header("Step 1: Context")

    target_role = st.text_input("Target Promotion Role")

    evidence_doc = st.text_area(
        "Evidence Document (Brag Doc / Promotion Packet / Achievements)",
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

# ----------------------
# STEP 2: Ask promotion question
# ----------------------

if st.session_state.step == 2:

    st.header("Step 2: Promotion Question")

    promotion_question = "How are you already operating at the next level?"

    st.write(f"**Question:** {promotion_question}")

    answer = st.text_area(
        "Your Answer",
        height=200
    )

    if st.button("Analyze Response"):

        prompt = f"""
You are evaluating a promotion readiness answer.

Promotion readiness signals:

1. Impact (measurable results)
2. Scope (ownership of large initiatives)
3. Influence (leadership, mentoring, driving decisions)
4. Next-level behavior (already operating at next level)

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
3. Extract supporting evidence from the evidence document that could strengthen the missing signals.
4. Keep the response concise.

Return output in this format:

Covered Signals:
- ...

Missing Signals:
- ...

Evidence the user could reference:
- ...
"""

        with st.spinner("Analyzing..."):

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You evaluate promotion readiness responses."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

        result = response.choices[0].message.content

        st.subheader("Analysis")
        st.write(result)

        feedback = st.radio(
            "Did this surface something you forgot to mention?",
            ["Yes", "No"]
        )

        if feedback:
            st.success("Thanks for the feedback!")
