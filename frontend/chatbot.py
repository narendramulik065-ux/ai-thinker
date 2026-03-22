import streamlit as st
import requests
import uuid
import time

st.set_page_config(
    page_title="Active Thinker",
    page_icon="🧠",
    layout="centered"
)

# ── Custom CSS — Top 1% UI ───────────────────────────────
st.markdown("""
<style>
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main container */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 750px;
}

/* Custom title card */
.title-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(99, 179, 237, 0.3);
}

.title-card h1 {
    font-size: 2.5rem;
    font-weight: 700;
    color: #63b3ed;
    margin: 0;
}

.title-card p {
    color: #a0aec0;
    margin: 0.5rem 0 0 0;
    font-size: 0.95rem;
}

/* Stats bar */
.stats-bar {
    display: flex;
    justify-content: space-between;
    background: #1a202c;
    border-radius: 12px;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1.5rem;
    border: 1px solid #2d3748;
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: #63b3ed;
}

.stat-label {
    font-size: 0.7rem;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* Subject badge */
.subject-badge {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
}

.badge-science    { background: #1a3a2a; color: #68d391; border: 1px solid #68d391; }
.badge-physics    { background: #1a2a3a; color: #63b3ed; border: 1px solid #63b3ed; }
.badge-chemistry  { background: #2a1a3a; color: #b794f4; border: 1px solid #b794f4; }
.badge-biology    { background: #2a2a1a; color: #f6e05e; border: 1px solid #f6e05e; }
.badge-mathematics{ background: #3a1a1a; color: #fc8181; border: 1px solid #fc8181; }
.badge-other      { background: #2a2a2a; color: #a0aec0; border: 1px solid #a0aec0; }

/* Lock card */
.lock-card {
    background: #1a202c;
    border: 1px solid #2d3748;
    border-left: 4px solid #e53e3e;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.5rem;
}

.lock-card h3 {
    color: #fc8181;
    margin: 0 0 0.3rem 0;
    font-size: 1rem;
}

.lock-card p {
    color: #718096;
    margin: 0;
    font-size: 0.85rem;
}

/* Hint card */
.hint-card {
    background: #1a202c;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.hint-item {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 0.8rem 0;
    border-bottom: 1px solid #2d3748;
}

.hint-item:last-child {
    border-bottom: none;
    padding-bottom: 0;
}

.hint-number {
    background: #2d3748;
    color: #63b3ed;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8rem;
    font-weight: 700;
    flex-shrink: 0;
    text-align: center;
    line-height: 28px;
}

.hint-text {
    color: #e2e8f0;
    font-size: 0.95rem;
    line-height: 1.5;
    padding-top: 3px;
}

/* Timer bar */
.timer-container {
    background: #1a202c;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 1rem;
    text-align: center;
}

/* Score card */
.score-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid #2d3748;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    text-align: center;
}

.score-number {
    font-size: 3.5rem;
    font-weight: 700;
    color: #63b3ed;
    line-height: 1;
}

.score-label {
    color: #718096;
    font-size: 0.85rem;
    margin-top: 0.3rem;
}

/* Metric cards */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.8rem;
    margin-bottom: 1.5rem;
}

.metric-card {
    background: #1a202c;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}

.metric-value {
    font-size: 1.3rem;
    font-weight: 700;
    color: #63b3ed;
}

.metric-label {
    font-size: 0.7rem;
    color: #718096;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.2rem;
}

/* Unlock card */
.unlock-card {
    background: linear-gradient(135deg, #1a2a1a, #0f2a1a);
    border: 1px solid #68d391;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.unlock-header {
    color: #68d391;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.unlock-content {
    color: #e2e8f0;
    font-size: 0.95rem;
    line-height: 1.7;
    border-left: 3px solid #68d391;
    padding-left: 1rem;
}

/* Integrity badge */
.integrity-genuine  { color: #68d391; }
.integrity-suspect  { color: #f6ad55; }
.integrity-copy     { color: #fc8181; }

/* Neuro points pop */
.points-pop {
    background: linear-gradient(135deg, #1a2a1a, #162616);
    border: 1px solid #48bb78;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
}

.points-number {
    font-size: 2rem;
    font-weight: 700;
    color: #68d391;
}

.points-label {
    color: #a0aec0;
    font-size: 0.85rem;
}
</style>
""", unsafe_allow_html=True)

BACKEND = "http://localhost:5000"

SUBJECT_BADGE_CLASS = {
    "SCIENCE":     "badge-science",
    "MATHEMATICS": "badge-mathematics",
    "ENGLISH":     "badge-other",
    "HISTORY":     "badge-other",
    "GEOGRAPHY":   "badge-other",
    "CIVICS":      "badge-other",
    "PHYSICS":     "badge-physics",
    "CHEMISTRY":   "badge-chemistry",
    "BIOLOGY":     "badge-biology",
    "OTHER":       "badge-other"
}

SUBJECT_EMOJI = {
    "SCIENCE":     "🔬",
    "MATHEMATICS": "🔢",
    "ENGLISH":     "📖",
    "HISTORY":     "📜",
    "GEOGRAPHY":   "🌍",
    "CIVICS":      "🏛️",
    "PHYSICS":     "⚡",
    "CHEMISTRY":   "🧪",
    "BIOLOGY":     "🌱",
    "OTHER":       "📚"
}

INTEGRITY_DISPLAY = {
    "genuine":        ("✅ Genuine",       "integrity-genuine"),
    "suspicious":     ("⚠️ Suspicious",    "integrity-suspect"),
    "paste_detected": ("🚫 Paste Detected","integrity-copy"),
    "direct_copy":    ("🚫 Direct Copy",   "integrity-copy"),
    "ai_generated":   ("🤖 AI Generated",  "integrity-copy"),
    "insufficient":   ("📝 Too Short",     "integrity-suspect")
}

# Session state
defaults = {
    "student_id":          str(uuid.uuid4())[:8],
    "phase":               "ask",
    "session_id":          None,
    "scaffold_qs":         [],
    "current_question":    "",
    "current_subject":     "OTHER",
    "neuro_points":        0,
    "last_result":         None,
    "student_answer":      "",
    "scaffold_start_time": None,
    "answer_start_time":   None,
    "thinking_time":       0,
    "grade":               "7"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

pts = st.session_state.neuro_points
level = "🔵 Passive Learner" if pts < 500 else \
        "🟡 Active Thinker"  if pts < 1500 else \
        "🟢 Deep Thinker"

# ── HEADER ───────────────────────────────────────────────
st.markdown(f"""
<div class="title-card">
    <h1>🧠 Active Thinker</h1>
    <p>Think first. Earn the answer. Build your mind.</p>
</div>
<div class="stats-bar">
    <div class="stat-item">
        <div class="stat-value">{st.session_state.student_id}</div>
        <div class="stat-label">Student ID</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">⚡ {pts}</div>
        <div class="stat-label">Neuro-Points</div>
    </div>
    <div class="stat-item">
        <div class="stat-value">{level}</div>
        <div class="stat-label">Level</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════
# PHASE 1 — ASK
# ════════════════════════════════════════════
if st.session_state.phase == "ask":
    st.markdown("### What do you want to learn today?")
    st.caption("Class 1 to 12 · All subjects · Maharashtra curriculum")

    grade = st.selectbox(
        "Your class:",
        ["1","2","3","4","5","6","7","8","9","10","11","12"],
        index=int(st.session_state.grade) - 1
    )
    st.session_state.grade = grade

    question = st.text_area(
        "Ask your question:",
        height=120,
        placeholder="Example: What is photosynthesis? / Explain Newton's laws / What caused World War 1?"
    )

    if st.button("Ask Active Thinker 🚀", type="primary", use_container_width=True):
        if question.strip():
            with st.spinner("Detecting subject and preparing your challenge..."):
                try:
                    res = requests.post(f"{BACKEND}/ask", json={
                        "question":   question.strip(),
                        "student_id": st.session_state.student_id,
                        "grade":      st.session_state.grade
                    }, timeout=30).json()

                    st.session_state.session_id          = res["session_id"]
                    st.session_state.scaffold_qs         = res["scaffold_questions"]
                    st.session_state.current_question    = question.strip()
                    st.session_state.current_subject     = res.get("subject", "OTHER")
                    st.session_state.scaffold_start_time = time.time()
                    st.session_state.phase               = "scaffold"
                    st.rerun()
                except Exception as e:
                    st.error(f"Connection failed. Is Flask running? Error: {e}")
        else:
            st.warning("Please type a question first!")


# ════════════════════════════════════════════
# PHASE 2 — SCAFFOLD + TIMER
# ════════════════════════════════════════════
elif st.session_state.phase == "scaffold":
    subject      = st.session_state.current_subject
    emoji        = SUBJECT_EMOJI.get(subject, "📚")
    badge_class  = SUBJECT_BADGE_CLASS.get(subject, "badge-other")

    st.markdown(f'<span class="subject-badge {badge_class}">{emoji} {subject}</span>',
                unsafe_allow_html=True)

    st.markdown(f"""
<div class="lock-card">
    <h3>🔒 Answer Locked</h3>
    <p>Think through these hints before writing your answer. The AI answer is hidden until you earn it.</p>
</div>
""", unsafe_allow_html=True)

    st.markdown(f"**Your question:** *{st.session_state.current_question}*")
    st.divider()

    # Hint cards
    hints_html = '<div class="hint-card">'
    for i, q in enumerate(st.session_state.scaffold_qs, 1):
        hints_html += f"""
        <div class="hint-item">
            <div class="hint-number">{i}</div>
            <div class="hint-text">{q}</div>
        </div>"""
    hints_html += '</div>'
    st.markdown(hints_html, unsafe_allow_html=True)

    # Timer gate
    MIN_THINKING = 45
    elapsed   = time.time() - (st.session_state.scaffold_start_time or time.time())
    remaining = max(0, MIN_THINKING - int(elapsed))

    if remaining > 0:
        progress = min(elapsed / MIN_THINKING, 1.0)
        st.markdown(f"""
<div class="timer-container">
    <p style="color:#f6ad55; font-weight:600; margin:0">
        ⏱️ Think carefully for <span style="font-size:1.3rem">{remaining}</span> more seconds...
    </p>
    <p style="color:#718096; font-size:0.8rem; margin:0.3rem 0 0 0">
        Use this time to think about the hints above
    </p>
</div>
""", unsafe_allow_html=True)
        st.progress(progress)
        time.sleep(1)
        st.rerun()

    st.markdown("### ✍️ Write your understanding:")
    student_answer = st.text_area(
        "Your answer:",
        height=200,
        placeholder="Write what YOU think the answer is, in your own words.\n\nTips:\n• Use simple language\n• Write 3-4 sentences minimum\n• Say 'I think...' or 'I believe...'\n• Don't copy from anywhere!",
        key="student_answer_input"
    )

    if student_answer and not st.session_state.answer_start_time:
        st.session_state.answer_start_time = time.time()

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Submit My Answer ✅", type="primary", use_container_width=True):
            if len(student_answer.strip()) >= 10:
                st.session_state.student_answer = student_answer
                st.session_state.thinking_time  = round(
                    time.time() - st.session_state.scaffold_start_time, 1
                )
                st.session_state.phase = "evaluate"
                st.rerun()
            else:
                st.warning("Write at least 2-3 sentences!")
    with col2:
        if st.button("New Question", use_container_width=True):
            st.session_state.phase               = "ask"
            st.session_state.scaffold_start_time = None
            st.session_state.answer_start_time   = None
            st.rerun()


# ════════════════════════════════════════════
# PHASE 3 — EVALUATE + REVEAL
# ════════════════════════════════════════════
elif st.session_state.phase == "evaluate":
    with st.spinner("Running NLP analysis..."):
        try:
            res = requests.post(f"{BACKEND}/evaluate", json={
                "session_id":     st.session_state.session_id,
                "student_answer": st.session_state.student_answer,
                "time_taken":     st.session_state.thinking_time
            }, timeout=15).json()
            st.session_state.last_result = res
            if res.get("integrity") == "genuine":
                st.session_state.neuro_points += res.get("neuro_points", 0)
        except Exception as e:
            st.error(f"Scoring failed: {e}")
            st.session_state.phase = "scaffold"
            st.rerun()

    result    = st.session_state.last_result
    score     = result["score"]
    subject   = result.get("subject", st.session_state.current_subject)
    emoji     = SUBJECT_EMOJI.get(subject, "📚")
    integrity = result.get("integrity", "genuine")
    int_label, int_class = INTEGRITY_DISPLAY.get(
        integrity, ("✅ Genuine", "integrity-genuine")
    )
    b = result.get("breakdown", {})

    # Subject + integrity row
    badge_class = SUBJECT_BADGE_CLASS.get(subject, "badge-other")
    st.markdown(
        f'<span class="subject-badge {badge_class}">{emoji} {subject}</span>'
        f'&nbsp;&nbsp;<span class="{int_class}" style="font-size:0.9rem">{int_label}</span>',
        unsafe_allow_html=True
    )

    # Score card
    score_color = "#68d391" if score >= 35 else "#f6ad55" if score >= 20 else "#fc8181"
    st.markdown(f"""
<div class="score-card">
    <div class="score-number" style="color:{score_color}">{score}</div>
    <div class="score-label">Cognitive Score out of 100</div>
</div>
""", unsafe_allow_html=True)

    st.progress(score / 100)

    # Metrics grid
    thinking = st.session_state.thinking_time
    think_badge = "🏆" if thinking > 90 else "✅" if thinking > 45 else "⚡"
    st.markdown(f"""
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-value">{b.get('semantic_similarity', 0)}%</div>
        <div class="metric-label">Concept Match</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{b.get('keyword_overlap', 0)}%</div>
        <div class="metric-label">Key Ideas</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{b.get('effort', 0)}/30</div>
        <div class="metric-label">Effort</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{b.get('originality', 100)}%</div>
        <div class="metric-label">Originality</div>
    </div>
</div>
<div class="metric-grid">
    <div class="metric-card" style="grid-column: span 4">
        <div class="metric-value">{think_badge} {thinking:.0f}s</div>
        <div class="metric-label">Time spent thinking</div>
    </div>
</div>
""", unsafe_allow_html=True)

    # Feedback
    if result.get("frustrated"):
        st.warning(result["feedback"])
    elif result["unlock"]:
        st.success(result["feedback"])
    elif integrity in ["paste_detected","direct_copy","ai_generated","suspicious"]:
        st.error(result["feedback"])
    else:
        st.info(result["feedback"])

    # Red flags
    red_flags = b.get("red_flags", [])
    if red_flags and integrity != "genuine":
        flag_messages = {
            "ai_opening_phrase":          "Answer starts with AI-typical phrases (Certainly!, Namaste beta!)",
            "heavy_ai_structure":         "Heavy use of AI formatting (firstly, secondly, in conclusion)",
            "markdown_formatting":        "Contains markdown formatting typical of AI output",
            "unnaturally_long_sentences": "Sentences are unusually long — typical of AI generation",
            "no_personal_voice":          "No personal writing voice detected",
            "sophisticated_vocabulary":   "Vocabulary too sophisticated for genuine student writing",
            "multiple_examples_ai_style": "Multiple structured examples — typical AI pattern",
            "paste_detected":             "Text appeared too quickly",
            "direct_copy_detected":       "Over 85% similar to source answer",
            "answer_too_short":           "Answer too short to evaluate"
        }
        with st.expander("Why was this flagged?"):
            for flag in red_flags:
                st.markdown(f"- {flag_messages.get(flag, flag)}")

    # Neuro-Points
    if integrity == "genuine":
        pts_earned = result['neuro_points']
        st.markdown(f"""
<div class="points-pop">
    <div class="points-number">+{pts_earned}</div>
    <div>
        <div class="points-label" style="font-weight:600; color:#68d391">Neuro-Points Earned</div>
        <div class="points-label">Total: ⚡ {st.session_state.neuro_points}</div>
    </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.warning("⚡ No Neuro-Points for copied answers. Write genuinely to earn points!")

    st.divider()

    # Unlock reveal
    if result["unlock"]:
        st.balloons()
        st.markdown(f"""
<div class="unlock-card">
    <div class="unlock-header">🔓 You earned it! Here is the full answer:</div>
    <div class="unlock-content">{result.get('gpt_answer', '')}</div>
</div>
<p style="color:#718096; font-size:0.8rem; text-align:center">
    Compare this with what you wrote. Notice what you got right and what you missed.
</p>
""", unsafe_allow_html=True)
    else:
        if integrity in ["paste_detected","direct_copy","ai_generated","suspicious"]:
            st.error("Answer not unlocked — write in your own words and try again.")
        else:
            st.error(f"Score needs to reach 35 to unlock. You got {score}. Keep trying!")
        if st.button("Try Again 🔄", type="primary"):
            st.session_state.phase               = "scaffold"
            st.session_state.scaffold_start_time = time.time()
            st.session_state.answer_start_time   = None
            st.rerun()

    if st.button("Ask a New Question ➡️", use_container_width=True):
        for k, v in defaults.items():
            if k not in ["student_id", "neuro_points", "grade"]:
                st.session_state[k] = v
        st.session_state.phase = "ask"
        st.rerun()