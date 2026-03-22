import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Active Thinker — Teacher Dashboard",
    page_icon="📊",
    layout="wide"
)

BACKEND = "http://localhost:5000"

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.dash-header {
    background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(99,179,237,0.3);
}
.dash-header h1 { color: #63b3ed; margin: 0; font-size: 1.8rem; }
.dash-header p  { color: #a0aec0; margin: 0.3rem 0 0 0; font-size: 0.9rem; }

.student-row {
    background: #1a202c;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    margin-bottom: 0.8rem;
    transition: border-color 0.2s;
}
.student-row:hover { border-color: #63b3ed; }

.level-badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}
.level-deep    { background:#1a2a1a; color:#68d391; border:1px solid #68d391; }
.level-active  { background:#2a2a1a; color:#f6e05e; border:1px solid #f6e05e; }
.level-passive { background:#1a2a3a; color:#63b3ed; border:1px solid #63b3ed; }

.stat-card {
    background: #1a202c;
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}
.stat-value { font-size: 1.8rem; font-weight: 700; color: #63b3ed; }
.stat-label { font-size: 0.7rem; color: #718096;
              text-transform: uppercase; letter-spacing: 0.05em; }

.section-title {
    font-size: 1.1rem; font-weight: 600;
    color: #e2e8f0; margin: 1.5rem 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #2d3748;
}

.trend-improving { color: #68d391; }
.trend-declining { color: #fc8181; }
.trend-stable    { color: #f6e05e; }
.trend-new       { color: #a0aec0; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────
st.markdown("""
<div class="dash-header">
    <h1>📊 Active Thinker — Teacher Dashboard</h1>
    <p>Real-time cognitive analytics · Class 1 to 12 · Maharashtra curriculum</p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# SECTION 1 — CLASS SUMMARY
# ════════════════════════════════════════════════════════
try:
    leaderboard = requests.get(f"{BACKEND}/leaderboard", timeout=10).json()
    connected   = True
except:
    leaderboard = []
    connected   = False

if not connected:
    st.error("Cannot connect to backend. Make sure Flask is running on port 5000.")
    st.stop()

total_students  = len(leaderboard)
avg_class_score = round(
    sum(s.get("avg_score", 0) or 0 for s in leaderboard) / max(total_students, 1), 1
)
total_sessions  = sum(s.get("sessions", 0) or 0 for s in leaderboard)
avg_thinking    = round(
    sum(s.get("avg_thinking_time", 0) or 0 for s in leaderboard) / max(total_students, 1), 1
)
deep_count      = sum(1 for s in leaderboard if "Deep"   in (s.get("level") or ""))
active_count    = sum(1 for s in leaderboard if "Active" in (s.get("level") or ""))

st.markdown('<div class="section-title">📈 Class Overview</div>',
            unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)
for col, val, lbl in [
    (c1, total_students,        "Total Students"),
    (c2, f"{avg_class_score}/100", "Class Avg Score"),
    (c3, total_sessions,        "Total Sessions"),
    (c4, f"{avg_thinking}s",    "Avg Thinking Time"),
    (c5, f"🟢{deep_count} 🟡{active_count}", "Deep / Active Thinkers")
]:
    col.markdown(f"""
    <div class="stat-card">
        <div class="stat-value">{val}</div>
        <div class="stat-label">{lbl}</div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# SECTION 2 — LEADERBOARD
# ════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🏆 Student Leaderboard — Ranked by Cognitive Effort</div>',
            unsafe_allow_html=True)
st.caption("Ranked by Neuro-Points — rewards thinking hard, not just being smart")

if not leaderboard:
    st.info("No students yet. Ask students to start using Active Thinker!")
else:
    for i, s in enumerate(leaderboard, 1):
        pts   = s.get("neuro_points", 0) or 0
        level = s.get("level", "Passive Learner")
        avg   = s.get("avg_score", 0) or 0
        sess  = s.get("sessions", 0) or 0
        think = s.get("avg_thinking_time", 0) or 0

        medal = "🥇" if i == 1 else "🥈" if i == 2 else \
                "🥉" if i == 3 else f"**{i}.**"

        if "Deep" in level:
            badge_class, level_display = "level-deep",    "🟢 Deep Thinker"
        elif "Active" in level:
            badge_class, level_display = "level-active",  "🟡 Active Thinker"
        else:
            badge_class, level_display = "level-passive", "🔵 Passive Learner"

        score_color = "#68d391" if avg >= 60 else \
                      "#f6e05e" if avg >= 40 else "#fc8181"

        col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2.5, 2, 1.5, 1.5, 1.5])
        col1.markdown(f"### {medal}")
        col2.markdown(
            f"**{s['student_id']}**<br>"
            f'<span class="level-badge {badge_class}">{level_display}</span>',
            unsafe_allow_html=True
        )
        col3.metric("⚡ Neuro-Points", f"{pts:,}")
        col4.metric("Avg Score",      f"{avg}/100")
        col5.metric("Sessions",       sess)
        col6.metric("Avg Think",      f"{think:.0f}s")

        st.markdown("<hr style='border-color:#2d3748; margin:0.5rem 0'>",
                    unsafe_allow_html=True)

# ════════════════════════════════════════════════════════
# SECTION 3 — STUDENT DETAIL
# ════════════════════════════════════════════════════════
st.markdown('<div class="section-title">👤 Individual Student Profile</div>',
            unsafe_allow_html=True)

student_id = st.text_input(
    "Enter Student ID:",
    placeholder="Copy from leaderboard above e.g. d88ef0a5"
)

if student_id.strip():
    try:
        data  = requests.get(
            f"{BACKEND}/stats/{student_id.strip()}", timeout=10
        ).json()
        total = data.get("total", 0)

        if total == 0:
            st.warning(f"No sessions found for: {student_id}")
        else:
            level = data.get("level", "Passive Learner")
            pts   = data.get("total_neuro_points", 0) or 0

            if "Deep" in level:
                bc, ld = "level-deep",    "🟢 Deep Thinker"
            elif "Active" in level:
                bc, ld = "level-active",  "🟡 Active Thinker"
            else:
                bc, ld = "level-passive", "🔵 Passive Learner"

            st.markdown(
                f'<span class="level-badge {bc}" '
                f'style="font-size:1rem;padding:0.4rem 1.2rem">{ld}</span>',
                unsafe_allow_html=True
            )
            st.markdown("")

            # Top metrics
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Questions Asked",    data["total"])
            c2.metric("Avg Score",          f"{data['avg_score']}/100")
            c3.metric("Unlocked",           data["unlocks"])
            c4.metric("Total Neuro-Points", f"⚡ {pts:,}")
            c5.metric("Avg Thinking",       f"{data['avg_thinking_time']}s")

            # ── Progress over time ───────────────────────
            history = data.get("score_history", [])
            if len(history) >= 2:
                st.markdown(
                    '<div class="section-title">📈 Score Progress Over Time</div>',
                    unsafe_allow_html=True
                )
                hist_df = pd.DataFrame(history)
                hist_df["session"] = range(1, len(hist_df) + 1)
                st.line_chart(
                    hist_df.set_index("session")["score"],
                    use_container_width=True
                )
                first = history[0]["score"]  or 0
                last  = history[-1]["score"] or 0
                diff  = round(last - first, 1)
                if diff > 0:
                    st.success(f"📈 Score improved by {diff} points since first session!")
                elif diff < 0:
                    st.warning(f"📉 Score dropped by {abs(diff)} points. Needs attention.")
                else:
                    st.info("Score is stable across sessions.")

            # ── Subject performance ──────────────────────
            profiles = data.get("cognitive_profile", [])
            if profiles:
                st.markdown(
                    '<div class="section-title">📚 Subject Performance</div>',
                    unsafe_allow_html=True
                )

                # Styled subject cards
                cols = st.columns(min(len(profiles), 3))
                for idx, p in enumerate(profiles):
                    trend_class = f"trend-{p['trend']}"
                    trend_arrow = "↑" if p["trend"] == "improving" else \
                                  "↓" if p["trend"] == "declining" else "→"
                    with cols[idx % 3]:
                        st.markdown(f"""
<div class="stat-card" style="text-align:left; margin-bottom:0.8rem">
    <div style="font-weight:600; color:#e2e8f0; margin-bottom:0.8rem">
        {p['subject']} · {p['sessions']} session{'s' if p['sessions']>1 else ''}
        <span class="{trend_class}" style="float:right">{trend_arrow} {p['trend']}</span>
    </div>
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.5rem">
        <div>
            <div style="font-size:1.2rem;font-weight:700;color:#63b3ed">{p['concept_score']}%</div>
            <div style="font-size:0.7rem;color:#718096">CONCEPT MATCH</div>
        </div>
        <div>
            <div style="font-size:1.2rem;font-weight:700;color:#68d391">{p['keyword_score']}%</div>
            <div style="font-size:0.7rem;color:#718096">KEY IDEAS</div>
        </div>
        <div>
            <div style="font-size:1.2rem;font-weight:700;color:#f6e05e">{p['effort_score']}/30</div>
            <div style="font-size:0.7rem;color:#718096">EFFORT</div>
        </div>
        <div>
            <div style="font-size:1.2rem;font-weight:700;color:#b794f4">{p['originality']}%</div>
            <div style="font-size:0.7rem;color:#718096">ORIGINALITY</div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

                # Multi-subject bar chart
                if len(profiles) > 1:
                    st.markdown(
                        '<div class="section-title">Concept Match by Subject</div>',
                        unsafe_allow_html=True
                    )
                    chart_df = pd.DataFrame({
                        "Subject":       [p["subject"] for p in profiles],
                        "Concept Match": [p["concept_score"] for p in profiles],
                        "Key Ideas":     [p["keyword_score"] for p in profiles],
                        "Effort (×3)":   [p["effort_score"] * 3 for p in profiles]
                    }).set_index("Subject")
                    st.bar_chart(chart_df, use_container_width=True)

            # ── Recent sessions ──────────────────────────
            recent = data.get("recent_sessions", [])
            if recent:
                st.markdown(
                    '<div class="section-title">📋 Recent Sessions</div>',
                    unsafe_allow_html=True
                )
                df = pd.DataFrame([{
                    "Question":     s["question"],
                    "Subject":      s.get("subject", ""),
                    "Score":        f"{s.get('score', 0)}/100",
                    "Unlocked":     "✅ Yes" if s.get("unlocked") else "❌ No",
                    "Integrity":    s.get("integrity", ""),
                    "Thinking (s)": round(s.get("thinking_time", 0) or 0, 0)
                } for s in recent])
                st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Error loading student data: {e}")

# ── Footer ───────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#4a5568;font-size:0.8rem'>"
    "Active Thinker v1.0 · RIT Hackathon 2K26 · AI for Social Good"
    "</p>",
    unsafe_allow_html=True
)