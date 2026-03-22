import sqlite3
from datetime import datetime

DB_PATH = "active_thinker.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            question TEXT,
            subject TEXT DEFAULT 'GENERAL',
            gpt_answer TEXT,
            scaffold_questions TEXT,
            student_answer TEXT,
            cognitive_score REAL,
            neuro_points INTEGER,
            unlocked INTEGER DEFAULT 0,
            integrity TEXT DEFAULT 'genuine',
            thinking_time REAL DEFAULT 0,
            paste_detected INTEGER DEFAULT 0,
            originality_score REAL DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT,
            grade TEXT,
            total_neuro_points INTEGER DEFAULT 0,
            level TEXT DEFAULT 'Passive Learner',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS cognitive_profile (
            student_id TEXT,
            subject TEXT,
            avg_concept_score REAL DEFAULT 0,
            avg_keyword_score REAL DEFAULT 0,
            avg_effort_score REAL DEFAULT 0,
            avg_originality REAL DEFAULT 100,
            sessions_count INTEGER DEFAULT 0,
            total_thinking_time REAL DEFAULT 0,
            trend TEXT DEFAULT 'new',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (student_id, subject)
        )
    """)

    conn.commit()
    conn.close()
    print("Database ready.")


def save_session(student_id, question, gpt_answer,
                 scaffold_qs, subject="GENERAL"):
    import json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Auto-create student record when they ask first question
    c.execute("INSERT OR IGNORE INTO students (id) VALUES (?)", (student_id,))

    c.execute("""
        INSERT INTO sessions
            (student_id, question, subject, gpt_answer, scaffold_questions)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, question, subject,
          gpt_answer, json.dumps(scaffold_qs)))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id


def update_session(session_id, student_answer, score, neuro_points,
                   unlocked, integrity="genuine", thinking_time=0,
                   paste_detected=False, originality_score=100):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE sessions SET
            student_answer=?, cognitive_score=?, neuro_points=?,
            unlocked=?, integrity=?, thinking_time=?,
            paste_detected=?, originality_score=?
        WHERE id=?
    """, (student_answer, score, neuro_points, int(unlocked),
          integrity, thinking_time, int(paste_detected),
          originality_score, session_id))
    conn.commit()
    conn.close()


def update_cognitive_profile(student_id, subject, breakdown):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT avg_concept_score, avg_keyword_score, avg_effort_score,
               avg_originality, sessions_count, total_thinking_time
        FROM cognitive_profile
        WHERE student_id=? AND subject=?
    """, (student_id, subject))
    row = c.fetchone()

    if row:
        n          = row[4]
        new_n      = n + 1
        new_concept  = ((row[0] * n) + breakdown.get("semantic_similarity", 0)) / new_n
        new_keyword  = ((row[1] * n) + breakdown.get("keyword_overlap", 0)) / new_n
        new_effort   = ((row[2] * n) + breakdown.get("effort", 0)) / new_n
        new_orig     = ((row[3] * n) + breakdown.get("originality", 100)) / new_n
        new_thinking = row[5] + breakdown.get("time_taken", 0)

        latest = (breakdown.get("semantic_similarity", 0) * 0.40 +
                  breakdown.get("keyword_overlap", 0) * 0.35 +
                  breakdown.get("effort", 0) * 0.25)
        prev   = (row[0] * 0.40 + row[1] * 0.35 + row[2] * 0.25)
        trend  = "improving" if latest > prev + 5 else \
                 "declining" if latest < prev - 5 else "stable"

        c.execute("""
            UPDATE cognitive_profile SET
                avg_concept_score=?, avg_keyword_score=?, avg_effort_score=?,
                avg_originality=?, sessions_count=?, total_thinking_time=?,
                trend=?, last_updated=CURRENT_TIMESTAMP
            WHERE student_id=? AND subject=?
        """, (round(new_concept, 1), round(new_keyword, 1),
              round(new_effort, 1), round(new_orig, 1),
              new_n, round(new_thinking, 1),
              trend, student_id, subject))
    else:
        c.execute("""
            INSERT INTO cognitive_profile (
                student_id, subject, avg_concept_score, avg_keyword_score,
                avg_effort_score, avg_originality, sessions_count,
                total_thinking_time, trend
            ) VALUES (?, ?, ?, ?, ?, ?, 1, ?, 'new')
        """, (student_id, subject,
              round(breakdown.get("semantic_similarity", 0), 1),
              round(breakdown.get("keyword_overlap", 0), 1),
              round(breakdown.get("effort", 0), 1),
              round(breakdown.get("originality", 100), 1),
              round(breakdown.get("time_taken", 0), 1)))

    conn.commit()
    conn.close()


def update_student_points(student_id, points_to_add):
    """
    FIXED: Level now upgrades correctly.
    Thresholds: 0-499 = Passive, 500-1499 = Active, 1500+ = Deep
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Ensure student exists
    c.execute("INSERT OR IGNORE INTO students (id) VALUES (?)", (student_id,))

    # Add points
    c.execute("""
        UPDATE students
        SET total_neuro_points = total_neuro_points + ?
        WHERE id = ?
    """, (points_to_add, student_id))

    # Read updated total and recalculate level
    c.execute("SELECT total_neuro_points FROM students WHERE id=?",
              (student_id,))
    row = c.fetchone()
    if row:
        pts = row[0] or 0
        if pts >= 1500:
            level = "Deep Thinker"
        elif pts >= 500:
            level = "Active Thinker"
        else:
            level = "Passive Learner"
        c.execute("UPDATE students SET level=? WHERE id=?",
                  (level, student_id))

    conn.commit()
    conn.close()


def get_stats(student_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT COUNT(*), AVG(cognitive_score), SUM(neuro_points),
               SUM(unlocked), AVG(thinking_time)
        FROM sessions WHERE student_id=?
    """, (student_id,))
    row = c.fetchone()

    c.execute("""
        SELECT question, subject, cognitive_score, unlocked,
               integrity, thinking_time, created_at
        FROM sessions WHERE student_id=?
        ORDER BY created_at DESC LIMIT 10
    """, (student_id,))
    recent = c.fetchall()

    c.execute("""
        SELECT subject, avg_concept_score, avg_keyword_score,
               avg_effort_score, sessions_count, trend, avg_originality
        FROM cognitive_profile WHERE student_id=?
    """, (student_id,))
    profiles = c.fetchall()

    c.execute("""
        SELECT level, total_neuro_points FROM students WHERE id=?
    """, (student_id,))
    student = c.fetchone()

    # Score history for progress chart
    c.execute("""
        SELECT cognitive_score, created_at
        FROM sessions
        WHERE student_id=? AND cognitive_score IS NOT NULL
        ORDER BY created_at ASC
        LIMIT 20
    """, (student_id,))
    history = c.fetchall()

    conn.close()

    return {
        "total":             row[0] or 0,
        "avg_score":         round(row[1] or 0, 1),
        "total_points":      row[2] or 0,
        "unlocks":           row[3] or 0,
        "avg_thinking_time": round(row[4] or 0, 1),
        "level":             student[0] if student else "Passive Learner",
        "total_neuro_points": student[1] if student else 0,
        "score_history": [
            {"score": h[0], "date": h[1]}
            for h in history
        ],
        "recent_sessions": [
            {
                "question":     r[0][:50] + "..." if len(r[0]) > 50 else r[0],
                "subject":      r[1],
                "score":        r[2],
                "unlocked":     r[3],
                "integrity":    r[4],
                "thinking_time": r[5],
                "date":         r[6]
            }
            for r in recent
        ],
        "cognitive_profile": [
            {
                "subject":       p[0],
                "concept_score": p[1],
                "keyword_score": p[2],
                "effort_score":  p[3],
                "sessions":      p[4],
                "trend":         p[5],
                "originality":   p[6]
            }
            for p in profiles
        ]
    }


def get_leaderboard():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT s.id, s.total_neuro_points, s.level,
               COUNT(sess.id)          as total_sessions,
               AVG(sess.cognitive_score) as avg_score,
               AVG(sess.thinking_time)  as avg_thinking
        FROM students s
        LEFT JOIN sessions sess ON s.id = sess.student_id
        GROUP BY s.id
        ORDER BY s.total_neuro_points DESC
        LIMIT 20
    """)
    rows = c.fetchall()
    conn.close()
    return [
        {
            "student_id":       r[0],
            "neuro_points":     r[1],
            "level":            r[2],
            "sessions":         r[3],
            "avg_score":        round(r[4] or 0, 1),
            "avg_thinking_time": round(r[5] or 0, 1)
        }
        for r in rows
    ]