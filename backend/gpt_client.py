import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Groq API key not found. Check your .env file.")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "llama-3.1-8b-instant"

SUBJECT_SCAFFOLD_STYLE = {
    "SCIENCE":     "Use simple real-world examples. Focus on observation, cause-effect, and basic concepts.",
    "MATHEMATICS": "Focus on step-by-step logic, number sense, and problem-solving approach.",
    "ENGLISH":     "Focus on meaning, grammar, vocabulary, and reading comprehension.",
    "HISTORY":     "Focus on events, causes, people involved, and their impact.",
    "GEOGRAPHY":   "Focus on location, climate, natural features, and human impact.",
    "CIVICS":      "Focus on rights, duties, government structure, and society.",
    "PHYSICS":     "Focus on principles, formulas, and cause-effect relationships.",
    "CHEMISTRY":   "Focus on reactions, properties, bonding, and molecular behavior.",
    "BIOLOGY":     "Focus on processes, functions, structures, and life mechanisms.",
    "OTHER":       "Use simple language. Focus on core concepts and real-world examples."
}

SUBJECT_EMOJIS = {
    "SCIENCE":     "🔬 SCIENCE",
    "MATHEMATICS": "🔢 MATHEMATICS",
    "ENGLISH":     "📖 ENGLISH",
    "HISTORY":     "📜 HISTORY",
    "GEOGRAPHY":   "🌍 GEOGRAPHY",
    "CIVICS":      "🏛️ CIVICS",
    "PHYSICS":     "⚡ PHYSICS",
    "CHEMISTRY":   "🧪 CHEMISTRY",
    "BIOLOGY":     "🌱 BIOLOGY",
    "OTHER":       "📚 GENERAL"
}


def detect_subject(question: str) -> str:
    q = question.lower()

    keyword_map = {
        "SCIENCE": [
            "plant", "animal", "water", "air", "soil", "seed", "leaf",
            "root", "food", "body", "sun", "moon", "star", "rain",
            "cloud", "river", "mountain", "weather", "season", "force",
            "magnet", "light", "sound", "heat", "electricity", "machine"
        ],
        "MATHEMATICS": [
            "number", "add", "subtract", "multiply", "divide", "fraction",
            "decimal", "equation", "calculate", "area", "volume", "angle",
            "triangle", "circle", "square", "percentage", "ratio",
            "algebra", "geometry", "theorem", "profit", "loss"
        ],
        "ENGLISH": [
            "noun", "verb", "adjective", "sentence", "grammar", "tense",
            "paragraph", "story", "poem", "essay", "meaning", "synonym",
            "antonym", "spelling", "punctuation", "comprehension", "write"
        ],
        "HISTORY": [
            "king", "queen", "war", "empire", "dynasty", "freedom",
            "independence", "gandhi", "mughal", "british", "revolution",
            "ancient", "medieval", "modern", "civilization", "ruler",
            "battle", "treaty", "history", "movement", "colonial"
        ],
        "GEOGRAPHY": [
            "map", "continent", "country", "state", "district", "river",
            "ocean", "climate", "rainfall", "desert", "forest", "crop",
            "population", "latitude", "longitude", "plateau", "delta",
            "soil type", "mineral", "transportation", "maharashtra"
        ],
        "CIVICS": [
            "government", "parliament", "constitution", "president",
            "prime minister", "election", "vote", "rights", "duties",
            "democracy", "court", "citizen", "panchayat",
            "municipality", "policy", "fundamental"
        ],
        "PHYSICS": [
            "motion", "newton", "velocity", "acceleration", "momentum",
            "gravity", "energy", "work", "power", "wave", "optics",
            "electric", "magnetic", "circuit", "current", "voltage",
            "thermodynamics", "pressure", "density", "friction", "inertia",
            "ohm", "ohms", "resistance", "conductor", "ampere",
            "volt", "watt", "charge", "capacitor", "inductor"
        ],
        "CHEMISTRY": [
            "acid", "base", "reaction", "element", "compound", "bond",
            "molecule", "atom", "periodic", "oxidation", "reduction",
            "organic", "carbon", "electron", "valence", "solution",
            "concentration", "mole", "catalyst", "polymer"
        ],
        "BIOLOGY": [
            "cell", "photosynthesis", "respiration", "dna", "rna",
            "protein", "enzyme", "hormone", "organ", "tissue",
            "evolution", "genetics", "chromosome", "mitosis", "meiosis",
            "ecosystem", "digestion", "blood", "heart", "bacteria", "virus"
        ]
    }

    scores = {
        subject: sum(1 for w in words if w in q)
        for subject, words in keyword_map.items()
    }

    best = max(scores, key=scores.get)
    if scores[best] > 0:
        return best

    try:
        subjects_list = ", ".join(keyword_map.keys()) + ", OTHER"
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content":
                f"Classify into exactly one word — {subjects_list}:\n{question}"}],
            max_tokens=10, temperature=0
        )
        result = response.choices[0].message.content.strip().upper()
        return result if result in keyword_map else "OTHER"
    except:
        return "OTHER"


def get_gpt_answer(question: str, grade: str = "general") -> str:
    """
    Get the real answer. LOCKED — never sent to student directly.
    FIXED: No greetings, no Namaste beta, no markdown formatting.
    Plain paragraphs only so detector doesn't flag our own answers.
    """
    if grade in ["1", "2", "3", "4"]:
        level_instruction = (
            "Explain to a Class 1-4 student aged 6-10. "
            "Use very simple short sentences. "
            "Use words a child understands. "
            "Maximum 3 short paragraphs."
        )
    elif grade in ["5", "6", "7", "8"]:
        level_instruction = (
            "Explain to a Class 5-8 student aged 10-14. "
            "Use clear simple language. "
            "Include one real-life example. "
            "Maximum 3 paragraphs."
        )
    else:
        level_instruction = (
            "Explain to a Class 9-12 student aged 14-18. "
            "Use proper academic language. "
            "Include the key formula or definition if relevant. "
            "Maximum 4 paragraphs."
        )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a teacher in rural Maharashtra, India. "
                        f"{level_instruction} "
                        "STRICT RULES — follow these exactly: "
                        "1. Do NOT start with any greeting like Namaste, Hello, Hi, Sure, Certainly. "
                        "2. Do NOT use markdown — no **, no ##, no bullet points with -, no numbered lists. "
                        "3. Start directly with the answer content. "
                        "4. Write in plain paragraphs only. "
                        "5. Do not end with questions to the student. "
                        "6. Be factual, clear, and complete."
                    )
                },
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Groq Error:", e)
        return "Error fetching answer. Please try again."


def get_scaffold_questions(question: str,
                            gpt_answer: str,
                            subject: str = "OTHER",
                            grade: str = "general") -> list:
    style = SUBJECT_SCAFFOLD_STYLE.get(subject, SUBJECT_SCAFFOLD_STYLE["OTHER"])

    if grade in ["1", "2", "3", "4"]:
        age_note = "The student is in Class 1-4 (age 6-10). Use very simple, fun questions. One sentence each."
    elif grade in ["5", "6", "7", "8"]:
        age_note = "The student is in Class 5-8 (age 10-14). Use simple clear questions."
    else:
        age_note = "The student is in Class 9-12 (age 14-18). Use proper academic questions."

    prompt = f"""A student asked: "{question}"
The correct answer is: "{gpt_answer}"
Subject: {subject}
{age_note}
Scaffolding style: {style}

Generate exactly 3 scaffolding questions that:
1. Guide the student toward understanding step by step
2. Do NOT reveal the answer
3. Are age-appropriate and simple
4. Progress from easier to harder

Return ONLY a JSON array of 3 strings.
Format: ["Question 1?", "Question 2?", "Question 3?"]
No extra text. Just the JSON array."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=250
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        questions = json.loads(text)
        if isinstance(questions, list) and len(questions) == 3:
            return questions
    except Exception as e:
        print("Scaffold Error:", e)

    return [
        "What do you already know about this topic?",
        "Can you think of an example from your daily life?",
        "What do you think the answer could be?"
    ]


def get_subject_badge(subject: str) -> str:
    return SUBJECT_EMOJIS.get(subject, "📚 GENERAL")