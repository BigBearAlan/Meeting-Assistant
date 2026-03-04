import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Promotion Readiness Gap Detector")

st.write(
"This tool analyzes a promotion answer and identifies missing evidence that could strengthen your case."
)

# User Inputs
target_role = st.text_input("Target Promotion Role")

evidence_doc = st.text_area(
    "Evidence Document (Brag Doc / Promotion Packet / Achievements)",
    height=200
)

answer = st.text_area(
    "Your Answer to the Promotion Question",
    height=200
)

if st.button("Analyze Response"):

    if not target_role or not evidence_doc or not answer:
        st.warning("Please fill in all fields.")
        st.stop()

    prompt = f"""
You are evaluating a promotion readiness answer.

Promotion readiness signals:

1. Impact (measurable results)
2. Scope (ownership of large initiatives)
3. Influence (leadership, mentoring, driving decisions)
4. Next-level behavior (already operating at next level)

Inputs:

Target Role:
{target_role}

Evidence Document:
{evidence_doc}

User Answer:
{answer}

Tasks:

1. Identify which readiness signals appear in the answer.
2. Identify which signals are missing.
3. Extract supporting evidence from the evidence document that could strengthen the missing signals.
4. Keep the answer very succinct. Keep only important information.

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

    st.subheader("Quick Feedback")
    feedback = st.radio(
        "Did this surface something you forgot to mention?",
        ["Yes", "No"]
    )

    if feedback:
        st.success("Thanks for the feedback!")
