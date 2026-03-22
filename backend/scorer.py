from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon', quiet=True)
nlp = spacy.load("en_core_web_sm")
sia = SentimentIntensityAnalyzer()


def tfidf_score(student_text: str, gpt_text: str) -> float:
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        matrix = vectorizer.fit_transform([student_text, gpt_text])
        score = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(score) * 100, 1)
    except:
        return 0.0


def keyword_score(student_text: str, gpt_text: str) -> float:
    gpt_doc = nlp(gpt_text.lower())
    student_doc = nlp(student_text.lower())
    gpt_keywords = set(
        chunk.text for chunk in gpt_doc.noun_chunks if len(chunk.text) > 3
    )
    student_keywords = set(
        chunk.text for chunk in student_doc.noun_chunks if len(chunk.text) > 3
    )
    if not gpt_keywords:
        return 0.0
    overlap = gpt_keywords.intersection(student_keywords)
    return round((len(overlap) / len(gpt_keywords)) * 100, 1)


def effort_score(student_text: str) -> float:
    words = student_text.lower().split()
    if len(words) < 3:
        return 0.0
    unique_words = set(words)
    vocab_richness = len(unique_words) / len(words)
    doc = nlp(student_text)
    sentence_count = len(list(doc.sents))
    score = (len(words) * 0.4) + (sentence_count * 3) + (vocab_richness * 10)
    return round(min(30, score), 1)


def is_frustrated(student_text: str) -> bool:
    sentiment = sia.polarity_scores(student_text)
    frustration_words = [
        "don't know", "dont know", "idk", "confused",
        "no idea", "hard", "difficult", "stuck", "help me"
    ]
    text_lower = student_text.lower()
    has_frustration = any(w in text_lower for w in frustration_words)
    return has_frustration or sentiment['compound'] < -0.3


def is_likely_pasted(answer: str, time_taken: float) -> bool:
    """
    Only flag as pasted if answer appeared in under 15 seconds total.
    Prevents false positives for fast typists who thought long.
    """
    word_count = len(answer.split())
    if word_count < 10:
        return False
    if time_taken > 15:
        return False
    words_per_second = word_count / max(time_taken, 0.5)
    return words_per_second > 2.0


def is_direct_copy(student_text: str, gpt_answer: str) -> bool:
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        matrix = vectorizer.fit_transform([student_text, gpt_answer])
        similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return similarity > 0.85
    except:
        return False


def detect_chatgpt_paste(student_text: str) -> dict:
    """
    Specifically detects ChatGPT/AI generated text pasted by students.
    Catches the attack: open ChatGPT → get answer → wait 200s → paste.
    The waiting time tricks the timer but the TEXT fingerprint betrays it.
    """
    text_lower = student_text.lower()
    text = student_text
    flags = []
    penalty = 0

    # Flag 1: ChatGPT opening phrases — instant giveaway
    ai_openers = [
        "certainly!", "sure!", "of course!", "great question",
        "namaste, beta", "namaste beta", "hello!", "hi there",
        "i'd be happy", "i would be happy", "let me explain",
        "let's explore", "today we're going to", "today, we're going to",
        "are you ready", "let's dive", "absolutely!", "indeed!",
        "welcome to", "in this lesson", "by the end of"
    ]
    if any(
        text_lower.startswith(o) or o in text_lower[:100]
        for o in ai_openers
    ):
        flags.append("ai_opening_phrase")
        penalty += 40

    # Flag 2: Heavy AI structural patterns
    ai_structure = [
        "here are", "here is a", "in summary", "in conclusion",
        "to summarize", "let's break it down", "let me break",
        "there are three", "there are two", "there are four",
        "there are five", "firstly,", "secondly,", "thirdly,",
        "lastly,", "first,", "second,", "third,", "finally,",
        "in other words", "that being said", "with that said",
        "it's worth noting", "it is worth noting",
        "it's important to note", "it is important to note",
        "key takeaway", "the key point", "to put it simply",
        "simply put,", "in layman's terms"
    ]
    struct_count = sum(1 for p in ai_structure if p in text_lower)
    if struct_count >= 3:
        flags.append("heavy_ai_structure")
        penalty += 35
    elif struct_count >= 2:
        flags.append("some_ai_structure")
        penalty += 15

    # Flag 3: Markdown formatting — ChatGPT always uses this
    markdown_patterns = ["**", "##", "###", "- ", "* ", "1. ", "2. ", "3. "]
    markdown_count = sum(1 for p in markdown_patterns if p in text)
    if markdown_count >= 3:
        flags.append("markdown_formatting")
        penalty += 30
    elif markdown_count >= 2:
        flags.append("some_markdown")
        penalty += 15
    # Flag 3: Bullet points or structured lists — students don't write like this
    bullet_patterns = ["* ", "• ", "- ", "→ ", "✓ "]
    bullet_count = sum(1 for p in bullet_patterns if p in text)
    if bullet_count >= 1:
        flags.append("bullet_point_formatting")
        penalty += 35  # strong signal — real students never use bullets

    # Flag 3b: Colon-introduced lists — "The heart works in two steps:"
    import re
    colon_list = re.findall(r'[A-Za-z\s]{5,30}:\s*\n', text)
    if len(colon_list) >= 1:
        flags.append("colon_list_structure")
        penalty += 25

    # Flag 3c: Em dash definitions — "Diastole – heart relaxes"
    em_dash_pattern = re.findall(r'\w+\s*[–—-]\s*\w+', text)
    if len(em_dash_pattern) >= 2:
        flags.append("em_dash_definitions")
        penalty += 30
    
    # Flag 10: Too many short separate paragraphs — AI formatting signature
    paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 10]
    short_paras = [p for p in paragraphs if len(p.split()) < 20]
    if len(short_paras) >= 3:
        flags.append("multiple_short_paragraphs")
        penalty += 25

    # Flag 4: Unnaturally long sentences
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
    if sentences:
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_len > 35:
            flags.append("unnaturally_long_sentences")
            penalty += 25
        elif avg_len > 25:
            flags.append("somewhat_long_sentences")
            penalty += 10

    # Flag 5: No personal voice whatsoever
    personal = [
        "i think", "i believe", "i know", "basically",
        "i understand", "i feel", "i guess", "i remember",
        "i learned", "in my opinion", "from what i",
        "i studied", "we learned", "our teacher",
        "in class", "i read", "i saw", "i heard",
        "mujhe lagta", "mala vatta"
    ]
    has_personal = any(p in text_lower for p in personal)
    word_count = len(text.split())
    if not has_personal and word_count > 30:
        flags.append("no_personal_voice")
        penalty += 25

    # Flag 6: Vocabulary too sophisticated for student
    tokens = [t.lower() for t in text.split() if t.isalpha()]
    if tokens:
        simple = [w for w in tokens if len(w) <= 4]
        simple_ratio = len(simple) / len(tokens)
        if simple_ratio < 0.20:
            flags.append("sophisticated_vocabulary")
            penalty += 20
        elif simple_ratio < 0.25:
            flags.append("somewhat_sophisticated")
            penalty += 10

    # Flag 7: Multiple AI-style examples
    example_patterns = [
        "for example,", "for instance,", "as an example",
        "consider this", "let's say", "suppose that",
        "imagine that", "take the case"
    ]
    example_count = sum(1 for p in example_patterns if p in text_lower)
    if example_count >= 2:
        flags.append("multiple_examples_ai_style")
        penalty += 15

    # Flag 8: Answer is longer than typical student response
    # Students write 50-150 words. AI writes 200-500 words.
    if word_count > 250:
        flags.append("unusually_long_answer")
        penalty += 20
    elif word_count > 180:
        flags.append("longer_than_typical")
        penalty += 10

    # Flag 9: Contains formula/calculation examples with numbers
    # ChatGPT always adds "For example, if V=12V and R=4Ω..."
    import re
    formula_pattern = re.findall(r'[A-Za-z]\s*=\s*[\d.]+', text)
    if len(formula_pattern) >= 2:
        flags.append("multiple_formula_examples")
        penalty += 15

    total_penalty = min(penalty, 100)
    originality   = max(0, 100 - total_penalty)
    is_ai         = total_penalty >= 50

    return {
        "originality_score": originality,
        "red_flags":         flags,
        "likely_copied":     is_ai,
        "ai_confidence":     total_penalty,
        "is_ai_generated":   is_ai
    }
    



def originality_score(student_text: str) -> dict:
    """Wrapper — calls ChatGPT detection engine."""
    return detect_chatgpt_paste(student_text)


def calculate_cognitive_score(student_answer: str,
                               gpt_answer: str,
                               question: str = "",
                               time_taken: float = 60.0,
                               paste_detected: bool = False) -> dict:

    # ── Guard: too short ─────────────────────────────────
    if not student_answer or len(student_answer.strip()) < 10:
        return {
            "score": 0, "unlock": False, "neuro_points": 0,
            "feedback": "Write at least 2-3 sentences to get scored!",
            "integrity": "insufficient", "frustrated": False,
            "breakdown": {
                "semantic_similarity": 0, "keyword_overlap": 0,
                "effort": 0, "originality": 0,
                "word_count": 0, "time_taken": time_taken,
                "red_flags": ["answer_too_short"]
            }
        }

    # ── Integrity Layer 1: paste speed ───────────────────
    if paste_detected or is_likely_pasted(student_answer, time_taken):
        return {
            "score": 0, "unlock": False, "neuro_points": 0,
            "feedback": "Your answer appeared very quickly — please write in your own words!",
            "integrity": "paste_detected", "frustrated": False,
            "breakdown": {
                "semantic_similarity": 0, "keyword_overlap": 0,
                "effort": 0, "originality": 0,
                "word_count": len(student_answer.split()),
                "time_taken": time_taken,
                "red_flags": ["paste_detected"]
            }
        }

    # ── Integrity Layer 2: direct copy of locked answer ──
    if is_direct_copy(student_answer, gpt_answer):
        return {
            "score": 5, "unlock": False, "neuro_points": 0,
            "feedback": "This looks very similar to the source answer. Try explaining in your own words!",
            "integrity": "direct_copy", "frustrated": False,
            "breakdown": {
                "semantic_similarity": 95, "keyword_overlap": 0,
                "effort": 0, "originality": 0,
                "word_count": len(student_answer.split()),
                "time_taken": time_taken,
                "red_flags": ["direct_copy_detected"]
            }
        }

    # ── Integrity Layer 3: ChatGPT paste detection ───────
    # Catches: open ChatGPT → wait 200s → paste
    # Timer tricks don't work — the TEXT fingerprint catches it
    ai_check = detect_chatgpt_paste(student_answer)

    # Also check length ratio — student can't write MORE than AI
    student_words = len(student_answer.split())
    gpt_words     = len(gpt_answer.split())
    length_suspicious = (
        student_words > gpt_words * 1.2
        and student_words > 150
        and ai_check["is_ai_generated"]
    )

    if length_suspicious or (ai_check["is_ai_generated"] and
                              ai_check["ai_confidence"] >= 60):
        return {
            "score": 0, "unlock": False, "neuro_points": 0,
            "feedback": (
                "Your answer looks like it was copied from ChatGPT or another AI. "
                "Write in your own words — shorter and simpler is perfectly fine! "
                "Just explain what YOU understand."
            ),
            "integrity": "ai_generated", "frustrated": False,
            "breakdown": {
                "semantic_similarity": 0, "keyword_overlap": 0,
                "effort": 0,
                "originality": ai_check["originality_score"],
                "word_count": student_words,
                "time_taken": time_taken,
                "red_flags": ai_check["red_flags"]
            }
        }

    # ── Core NLP signals ─────────────────────────────────
    orig = ai_check  # reuse already computed result
    s1   = tfidf_score(student_answer, gpt_answer)
    s2   = keyword_score(student_answer, gpt_answer)
    s3   = effort_score(student_answer)

    # Normalize effort 0-30 → 0-100
    s3_normalized = (s3 / 30) * 100

    # Weighted formula
    base_score = (s1 * 0.40) + (s2 * 0.25) + (s3_normalized * 0.35)

    # Originality multiplier — min 0.7 so genuine students not punished hard
    orig_multiplier = orig["originality_score"] / 100
    final_score = base_score * (0.7 + (orig_multiplier * 0.3))
    final_score = round(min(100, final_score), 1)

    # Define integrity BEFORE using it
    integrity = "suspicious" if orig["likely_copied"] else "genuine"

    # Exceptional thinker bonus
    if s3 >= 28 and s1 >= 30 and integrity == "genuine":
        final_score = max(final_score, 40.0)

    # Unlock threshold
    unlock      = final_score >= 35 and integrity == "genuine"
    neuro_points = int(final_score * 1.5) if integrity == "genuine" else 0
    frustrated   = is_frustrated(student_answer)

    # Feedback
    prefix = "Your answer seems copied. " if integrity == "suspicious" else ""

    if frustrated:
        feedback = "It's okay to find this hard! Write even one thing you know about this topic."
    elif final_score >= 70:
        feedback = prefix + "Outstanding thinking! Very close to the complete answer."
    elif final_score >= 55:
        feedback = prefix + "Great effort — you've earned the answer! Compare with what you wrote."
    elif final_score >= 35:
        feedback = prefix + "Good thinking! You earned it — see what you missed."
    elif final_score >= 20:
        feedback = prefix + "You're on the right track! Add more detail about key concepts."
    else:
        feedback = prefix + "Keep going! Write more of what you already know."

    if integrity == "suspicious" and base_score >= 35:
        feedback = "Your content is good — but rewrite it in YOUR OWN WORDS. You'll unlock it!"

    return {
        "score":      final_score,
        "unlock":     unlock,
        "neuro_points": neuro_points,
        "feedback":   feedback,
        "integrity":  integrity,
        "frustrated": frustrated,
        "breakdown": {
            "semantic_similarity": s1,
            "keyword_overlap":     s2,
            "effort":              s3,
            "originality":         orig["originality_score"],
            "word_count":          student_words,
            "time_taken":          round(time_taken, 1),
            "red_flags":           orig["red_flags"]
        }
    }