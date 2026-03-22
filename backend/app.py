import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import (init_db, save_session, update_session,
                      update_cognitive_profile, update_student_points,
                      get_stats, get_leaderboard)
from gpt_client import get_gpt_answer, get_scaffold_questions, detect_subject
from scorer import calculate_cognitive_score

app = Flask(__name__)
CORS(app)
init_db()


@app.route("/")
def home():
    return "Active Thinker Backend is Running 🚀"


@app.route("/ask", methods=["POST"])
def ask():
    data       = request.get_json()
    question   = data.get("question", "").strip()
    student_id = data.get("student_id", "anonymous")
    grade      = data.get("grade", "general")

    if not question:
        return jsonify({"error": "No question provided"}), 400

    subject    = detect_subject(question)
    gpt_answer = get_gpt_answer(question, grade)
    scaffold_qs = get_scaffold_questions(question, gpt_answer, subject, grade)
    session_id  = save_session(student_id, question, gpt_answer,
                               scaffold_qs, subject)

    return jsonify({
        "session_id":        session_id,
        "scaffold_questions": scaffold_qs,
        "subject":           subject,
        "message":           "Think first! Answer the questions above to unlock the full answer."
    })


@app.route("/evaluate", methods=["POST"])
def evaluate():
    data           = request.get_json()
    session_id     = data.get("session_id")
    student_answer = data.get("student_answer", "").strip()
    time_taken     = float(data.get("time_taken", 60.0))

    if not session_id:
        return jsonify({"error": "No session ID"}), 400

    conn = sqlite3.connect("active_thinker.db")
    c    = conn.cursor()
    c.execute("""
        SELECT gpt_answer, question, student_id, subject
        FROM sessions WHERE id=?
    """, (session_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Session not found"}), 404

    gpt_answer, question, student_id, subject = row

    result = calculate_cognitive_score(
        student_answer=student_answer,
        gpt_answer=gpt_answer,
        question=question,
        time_taken=time_taken
    )

    update_session(
        session_id=session_id,
        student_answer=student_answer,
        score=result["score"],
        neuro_points=result["neuro_points"],
        unlocked=result["unlock"],
        integrity=result["integrity"],
        thinking_time=time_taken,
        paste_detected=(result["integrity"] == "paste_detected"),
        originality_score=result["breakdown"].get("originality", 100)
    )

    if result["integrity"] == "genuine":
        update_cognitive_profile(student_id, subject, result["breakdown"])
        update_student_points(student_id, result["neuro_points"])

    response = {
        "score":       result["score"],
        "neuro_points": result["neuro_points"],
        "feedback":    result["feedback"],
        "unlock":      result["unlock"],
        "integrity":   result["integrity"],
        "frustrated":  result["frustrated"],
        "subject":     subject,
        "breakdown":   result["breakdown"]
    }

    if result["unlock"]:
        response["gpt_answer"] = gpt_answer

    return jsonify(response)


@app.route("/stats/<student_id>", methods=["GET"])
def stats(student_id):
    return jsonify(get_stats(student_id))


@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    return jsonify(get_leaderboard())


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "Active Thinker backend running ✓"})


if __name__ == "__main__":
    app.run(debug=True, port=5000)