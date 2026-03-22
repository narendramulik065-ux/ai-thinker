import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Why Active Thinker",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Why Active Thinker Exists")
st.caption("Primary research — Class 6 to 12 students, Sangli, Maharashtra — March 2026")
st.divider()

# ── UPDATE THESE WITH YOUR REAL SURVEY NUMBERS ──────────
SURVEY_N           = 34
AI_DAILY           = 91
COPIED_DIRECTLY    = 78
FORGOT_IN_10_MIN   = 83
WOULD_USE          = 71
THINKING_DECREASED = 67
TEACHERS_TOLD      = 74

# ── UPDATE WITH REAL VERBATIM QUOTES FROM STUDENTS ──────
QUOTES = [
    ("I get the answer from ChatGPT but in the exam I blank out completely.",
     "Class 12, NEET aspirant, Sangli"),
    ("I know I'm becoming lazy but there's no alternative when time is short.",
     "Class 12, JEE aspirant, Sangli"),
    ("If it actually helps me remember, I'll use it every day for sure.",
     "Class 11, MHT-CET, Sangli"),
]

# ── UPDATE WITH ACTUAL Q10 RESPONSES ────────────────────
TOP_REASONS = {
    "Helps me actually remember concepts":  82,
    "Score improves — see my progress":     76,
    "Works for all school subjects":        71,
    "Tells me where my understanding fails":68,
    "Earn points for thinking harder":      59,
    "Works for Class 1 to 12":             55,
    "Works offline on slow internet":       53,
}

# ── KEY METRICS ──────────────────────────────────────────
st.subheader(f"What {SURVEY_N} real students told us")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Use AI daily",             f"{AI_DAILY}%",
          f"of {SURVEY_N} students")
c2.metric("Copy answers directly",    f"{COPIED_DIRECTLY}%",
          "no real learning")
c3.metric("Forgot in 10 minutes",     f"{FORGOT_IN_10_MIN}%",
          "after reading AI")
c4.metric("Thinking decreased",       f"{THINKING_DECREASED}%",
          "self-reported")
c5.metric("Teachers warned them",     f"{TEACHERS_TOLD}%",
          "to stop using AI")
c6.metric("Would use Active Thinker", f"{WOULD_USE}%",
          "said yes or maybe")

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("In their own words")
    for quote, source in QUOTES:
        st.markdown(f"> *\"{quote}\"*")
        st.caption(f"— {source}")
        st.markdown("")

with right:
    st.subheader("What would make them use it daily")
    df = pd.DataFrame({
        "Feature":       list(TOP_REASONS.keys()),
        "Students (%)":  list(TOP_REASONS.values())
    }).sort_values("Students (%)", ascending=True)
    st.bar_chart(df.set_index("Feature"))

st.divider()

# ── THE PROBLEM VISUALIZED ───────────────────────────────
st.subheader("The real crisis — across every class, every subject")

col1, col2 = st.columns(2)
with col1:
    st.error(
        f"**{FORGOT_IN_10_MIN}% of students** — from Class 6 to Class 12 — "
        f"forgot the AI answer within 10 minutes of reading it.\n\n"
        f"They got the answer. They learned nothing."
    )
with col2:
    st.success(
        "**Active Thinker** protects the Confusion Window for every student — "
        "Class 1 to 12, rural and urban Maharashtra, all subjects.\n\n"
        "A Class 1 child asking why the sky is blue gets the same cognitive "
        "protection as a Class 12 student preparing for board exams."
    )

st.divider()

# ── WHO WE SERVE ─────────────────────────────────────────
st.subheader("Who Active Thinker serves")
col1, col2, col3 = st.columns(3)
with col1:
    st.info(
        "**Class 1 – 4** 🧒\n\n"
        "Simple science and maths questions.\n"
        "Fun, age-appropriate hints.\n"
        "Builds curiosity early."
    )
with col2:
    st.info(
        "**Class 5 – 8** 📚\n\n"
        "All subjects — Science, History,\n"
        "Geography, English, Maths.\n"
        "Builds deep understanding."
    )
with col3:
    st.info(
        "**Class 9 – 12** 🎯\n\n"
        "Board exam + competitive prep.\n"
        "Physics, Chemistry, Biology, Maths.\n"
        "Earns the answer through thinking."
    )

st.divider()
st.caption(
    f"Survey conducted in person at a coaching academy, Sangli, Maharashtra. "
    f"n={SURVEY_N} students, Class 6–12. Anonymous responses. March 2026."
)