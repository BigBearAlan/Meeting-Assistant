import streamlit as st

st.title("Promotion Readiness Practice")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1

# ---------------------------
# STEP 1 — Promotion Context
# ---------------------------

if st.session_state.step == 1:

    st.header("Step 1: Promotion Context")

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


# ---------------------------
# STEP 2 — Promotion Question
# ---------------------------

elif st.session_state.step == 2:

    st.header("Step 2: Promotion Question")

    promotion_question = "How are you already operating at the next level?"

    st.write(f"**Question:** {promotion_question}")

    answer = st.text_area(
        "Your Answer",
        height=200
    )

    if st.button("Analyze Response"):

        if not answer:
            st.warning("Please write your answer first.")
            st.stop()

        with st.spinner("Analyzing..."):

            # MOCK ANALYSIS (no API call)
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

        st.subheader("Analysis")
        st.write(result)

        feedback = st.radio(
            "Did this surface something you forgot to mention?",
            ["Yes", "No"]
        )

        if feedback:
            st.success("Thanks for the feedback!")

        if st.button("Restart"):
            st.session_state.step = 1
            st.rerun()
