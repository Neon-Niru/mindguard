"""Deterministic fact extraction from student messages.

This module only records facts that are explicitly supported by the
student's own words. It never invents values (for example, it no longer
guesses attendance from sleep hours) and it prefers the most recent
sentence about a topic so corrections override earlier answers.
"""

import re


def _sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [part.strip() for part in parts if part.strip()]


def _has_any(text, phrases):
    for phrase in phrases:
        pattern = r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])"
        if re.search(pattern, text):
            return True
    return False


def _matching_sentences(sentences, phrases):
    return [sentence for sentence in sentences if _has_any(sentence, phrases)]


def _latest_context(sentences, phrases):
    matches = _matching_sentences(sentences, phrases)
    return matches[-1].lower() if matches else ""


def _all_context(sentences, phrases):
    matches = _matching_sentences(sentences, phrases)
    return " ".join(matches).lower()


def _last_number(pattern, text):
    matches = list(re.finditer(pattern, text))
    if not matches:
        return None
    match = matches[-1]
    try:
        if match.lastindex and match.lastindex >= 2 and match.group(2):
            return (float(match.group(1)) + float(match.group(2))) / 2
        return float(match.group(1))
    except (TypeError, ValueError):
        return None


def _extract_hours(text, subject_phrases):
    """Extract an hour value tied to a subject, preferring explicit matches."""
    if not _has_any(text, subject_phrases):
        return None

    range_pattern = r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)"
    subject = "|".join(re.escape(phrase) for phrase in subject_phrases)
    before_pattern = (
        rf"(?:{subject})[^.\n]{{0,30}}?(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)"
    )
    after_pattern = (
        rf"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)\s*(?:of\s+)?(?:{subject})"
    )
    plain_pattern = r"(\d+(?:\.\d+)?)\s*(?:hours?|hrs?)"

    for pattern in (range_pattern, before_pattern, after_pattern):
        value = _last_number(pattern, text)
        if value is not None:
            return value

    return _last_number(plain_pattern, text)


def _extract_attendance(text):
    patterns = [
        r"attendance\s*(?:is|was|at|around|about)?\s*(\d{1,3})\s*%",
        r"(\d{1,3})\s*%\s*(?:attendance|attending|classes|school)",
        r"attend\s*(?:about|around)?\s*(\d{1,3})\s*%",
    ]
    for pattern in patterns:
        value = _last_number(pattern, text)
        if value is not None:
            return max(0, min(100, value))
    return None


SLEEP_TRIGGERS = [
    "sleep", "sleeping", "slept", "bed", "bedtime", "insomnia", "nap",
    "wake up", "woke up", "waking up", "rested", "resting",
]

ACADEMIC_TRIGGERS = [
    "study", "studying", "studied", "exam", "exams", "test", "tests",
    "assignment", "assignments", "homework", "class", "classes", "school",
    "college", "academic", "grade", "grades", "project", "projects",
    "syllabus", "semester",
]


def extract_facts(text: str):
    facts = {}
    text = text or ""
    sentences = _sentences(text)

    # -------------------------
    # Sleep
    # -------------------------
    sleep_context = _all_context(sentences, SLEEP_TRIGGERS)

    if sleep_context:
        sleep = {}

        hours = _extract_hours(sleep_context, ["sleep", "sleeping", "slept", "bed"])
        if hours is not None:
            sleep["hours"] = max(3, min(10, hours))

        quality_context = _latest_context(sentences, SLEEP_TRIGGERS)
        if _has_any(quality_context, ["poor", "bad", "terrible", "awful", "not good", "restless", "broken"]):
            sleep["quality"] = "Poor"
        elif _has_any(quality_context, ["good", "great", "well", "deep"]):
            sleep["quality"] = "Good"
        elif _has_any(quality_context, ["okay", "ok", "decent", "fair", "fine", "alright"]):
            sleep["quality"] = "Fair"

        if _has_any(sleep_context, [
            "tired", "exhausted", "drained", "not rested", "wake up tired",
            "woke up tired", "waking up tired", "never rested", "wiped out",
        ]):
            sleep["rested"] = "Rarely"
        elif _has_any(sleep_context, ["well rested", "fully rested", "refreshed", "rested"]):
            sleep["rested"] = "Often"

        if _has_any(sleep_context, [
            "irregular", "inconsistent", "different times", "no set time",
            "changes every night", "can't sleep", "cannot sleep",
        ]):
            sleep["consistency"] = "Irregular"
        elif _has_any(sleep_context, ["regular", "same time", "consistent", "routine"]):
            sleep["consistency"] = "Regular"

        if sleep:
            facts["sleep"] = sleep

    # -------------------------
    # Academic Load
    # -------------------------
    academic_context = _all_context(sentences, ACADEMIC_TRIGGERS)

    if academic_context:
        acad = {}

        hours = _extract_hours(
            academic_context,
            ["study", "studying", "studied", "homework", "class", "classes", "schoolwork"],
        )
        if hours is not None:
            acad["study_hours"] = max(0, min(16, hours))

        latest_academic = _latest_context(sentences, ACADEMIC_TRIGGERS)

        if _has_any(latest_academic, [
            "overwhelming", "overwhelmed", "too much", "heavy", "excessive",
            "a lot", "piled up", "loads of", "constant assignments",
        ]):
            acad["homework_load"] = "Heavy"
        elif _has_any(latest_academic, [
            "light", "manageable", "easy", "not much", "little", "under control",
        ]):
            acad["homework_load"] = "Light"
        elif _has_any(latest_academic, [
            "moderate", "okay", "ok", "fine", "some", "normal", "average",
        ]):
            acad["homework_load"] = "Moderate"

        assignment_context = _all_context(sentences, ["assignment", "assignments"])
        if assignment_context:
            if _has_any(assignment_context, ["many", "several", "lots", "ton of", "loads of"]):
                acad["assignments"] = "Several"
            elif _has_any(assignment_context, ["no assignments", "none", "finished all"]):
                acad["assignments"] = "None"
            elif _has_any(assignment_context, ["few", "one", "a couple", "single"]):
                acad["assignments"] = "A few"
            else:
                acad["assignments"] = "Sometimes"

        project_context = _all_context(sentences, ["project", "projects"])
        if project_context:
            if _has_any(project_context, ["many", "several", "lots", "multiple"]):
                acad["projects"] = "Several"
            else:
                acad["projects"] = "A few"

        exam_context = _all_context(sentences, ["exam", "exams", "test", "tests", "finals"])
        if exam_context:
            if _has_any(exam_context, ["exam week", "every week", "many", "multiple", "finals", "constant"]):
                acad["upcoming_exams"] = "Often"
            elif _has_any(exam_context, ["one exam", "a test", "single"]):
                acad["upcoming_exams"] = "A few"
            else:
                acad["upcoming_exams"] = "Sometimes"

        difficulty_context = _all_context(sentences, [
            "difficult", "hard to", "is hard", "are hard", "was hard",
            "struggling", "struggle with", "tough", "confusing",
        ])
        if difficulty_context and _has_any(difficulty_context, ["subject", "math", "science", "class", "course", "topic"]):
            acad["subject_difficulty"] = "High"
        elif _has_any(latest_academic, ["easy", "simple", "not hard"]):
            acad["subject_difficulty"] = "Low"

        expectation_context = _all_context(sentences, [
            "expectation", "expectations", "parents expect", "pressure", "pressure from",
        ])
        if expectation_context:
            if _has_any(expectation_context, ["high", "a lot", "constant", "too much", "heavy"]):
                acad["academic_expectations"] = "High"
            elif _has_any(expectation_context, ["low", "no pressure", "not much"]):
                acad["academic_expectations"] = "Low"

        attendance = _extract_attendance(academic_context)
        if attendance is not None:
            acad["attendance"] = attendance

        if acad:
            facts["academic_load"] = acad

    # -------------------------
    # Emotional Exhaustion
    # -------------------------
    exhaustion_context = _latest_context(sentences, [
        "drained", "exhausted", "burnout", "burnt out", "overwhelmed",
        "can't cope", "cannot cope", "emotionally", "wiped out",
    ])
    recovery_context = _all_context(sentences, [
        "recover", "rest", "rested", "tired", "sleep",
    ])

    if exhaustion_context:
        exhaustion = {}

        if _has_any(exhaustion_context, ["always", "every day", "constantly", "all the time"]):
            exhaustion["feeling_drained"] = "Always"
        elif _has_any(exhaustion_context, ["drained", "exhausted", "wiped out", "burnout", "burnt out"]):
            exhaustion["feeling_drained"] = "Often"
        elif _has_any(exhaustion_context, ["sometimes", "occasionally"]):
            exhaustion["feeling_drained"] = "Sometimes"

        if _has_any(recovery_context, [
            "not rested", "wake up tired", "woke up tired", "still tired",
            "no recovery", "doesn't help", "does not help", "cannot recover",
            "can't recover",
        ]):
            exhaustion["recovery_after_rest"] = "Rarely"
        elif _has_any(recovery_context, ["recover", "rest helps", "feel better after"]):
            exhaustion["recovery_after_rest"] = "Often"

        if exhaustion:
            facts["emotional_exhaustion"] = exhaustion

    # -------------------------
    # Burnout Symptoms
    # -------------------------
    symptom_context = _latest_context(sentences, [
        "overwhelmed", "overwhelming", "burnout", "burnt out", "can't do this",
        "cannot do this", "giving up", "hopeless", "lost interest",
        "don't care", "do not care", "not interested",
    ])

    if symptom_context:
        symptoms = {}

        if _has_any(symptom_context, ["always", "every day", "constantly"]):
            symptoms["overwhelmed"] = "Always"
        elif _has_any(symptom_context, ["overwhelmed", "overwhelming", "can't do this", "hopeless"]):
            symptoms["overwhelmed"] = "Often"

        if _has_any(symptom_context, ["lost interest", "don't care", "do not care", "not interested", "no interest"]):
            symptoms["loss_of_interest"] = "Often"

        if symptoms:
            facts["burnout_symptoms"] = symptoms

    # -------------------------
    # Motivation
    # -------------------------
    motivation_context = _latest_context(sentences, [
        "motivated", "motivation", "unmotivated", "procrastinating",
        "procrastinate", "procrastination", "can't start", "cannot start",
        "don't feel like", "do not feel like",
    ])

    if motivation_context:
        if _has_any(motivation_context, [
            "no motivation", "unmotivated", "can't start", "cannot start",
            "struggling", "don't feel like", "do not feel like", "procrastinating", "procrastinate",
        ]):
            facts["motivation"] = {"study_motivation": "Low"}
        elif _has_any(motivation_context, ["very motivated", "highly motivated", "love studying", "excited"]):
            facts["motivation"] = {"study_motivation": "Good"}
        else:
            facts["motivation"] = {"study_motivation": "Moderate"}

    # -------------------------
    # Cognitive
    # -------------------------
    cognitive_context = _latest_context(sentences, [
        "concentrate", "concentration", "focus", "distracted", "brain fog",
        "memory", "forget", "forgetful", "remember",
    ])

    if cognitive_context:
        cognitive = {}

        if _has_any(cognitive_context, [
            "can't focus", "cannot focus", "can't concentrate", "cannot concentrate",
            "poor focus", "poor concentration", "brain fog", "distracted", "difficult to focus",
        ]):
            cognitive["concentration"] = "Poor"
        elif _has_any(cognitive_context, ["good focus", "focus well", "concentrate well", "good concentration"]):
            cognitive["concentration"] = "Good"
        elif _has_any(cognitive_context, ["concentrate", "concentration", "focus"]):
            cognitive["concentration"] = "Fair"

        if _has_any(cognitive_context, [
            "forget", "forgetful", "memory is bad", "poor memory", "can't remember", "cannot remember",
        ]):
            cognitive["memory"] = "Poor"
        elif _has_any(cognitive_context, ["good memory", "remember well"]):
            cognitive["memory"] = "Good"

        if cognitive:
            facts["cognitive"] = cognitive

    # -------------------------
    # Stress
    # -------------------------
    stress_context = _latest_context(sentences, ["stress", "stressed", "pressure", "tense", "overwhelmed"])

    if stress_context:
        stress = {}

        if _has_any(stress_context, ["no stress", "not stressed", "low stress", "low"]):
            stress["stress_frequency"] = "Low"
        elif _has_any(stress_context, ["very stressed", "high stress", "extremely", "constant", "all the time", "overwhelming"]):
            stress["stress_frequency"] = "High"
        else:
            stress["stress_frequency"] = "Moderate"

        if _has_any(stress_context, [
            "can't control", "cannot control", "out of control", "overwhelming",
            "too much", "can't manage", "cannot manage", "can't cope", "cannot cope",
        ]):
            stress["stress_control"] = "Low"
        elif _has_any(stress_context, ["manage", "control", "cope", "handle"]):
            stress["stress_control"] = "Good"

        facts["stress"] = stress

    # -------------------------
    # Anxiety
    # -------------------------
    anxiety_context = _latest_context(sentences, [
        "anxious", "anxiety", "worry", "worried", "worrying", "nervous", "panic",
    ])

    if anxiety_context:
        if _has_any(anxiety_context, ["always", "constantly", "every day", "all the time"]):
            facts["anxiety"] = {"worry_frequency": "Always"}
        elif _has_any(anxiety_context, ["often", "a lot"]):
            facts["anxiety"] = {"worry_frequency": "Often"}
        else:
            facts["anxiety"] = {"worry_frequency": "Sometimes"}

    # -------------------------
    # Mood
    # -------------------------
    mood_context = _latest_context(sentences, [
        "mood", "sad", "happy", "down", "depressed", "irritable", "miserable",
        "feeling low", "feel low", "upset",
    ])

    if mood_context:
        if _has_any(mood_context, ["sad", "down", "low", "depressed", "irritable", "miserable", "upset"]):
            facts["mood"] = {"positive_mood": "Poor"}
        elif _has_any(mood_context, ["happy", "good", "great", "positive"]):
            facts["mood"] = {"positive_mood": "Good"}
        elif _has_any(mood_context, ["okay", "ok", "fine", "neutral", "average"]):
            facts["mood"] = {"positive_mood": "Fair"}

    # -------------------------
    # Productivity
    # -------------------------
    productivity_context = _latest_context(sentences, [
        "productive", "productivity", "task", "tasks", "deadline", "deadlines",
        "efficient", "get things done", "on top of",
    ])

    if productivity_context:
        if _has_any(productivity_context, [
            "can't complete", "cannot complete", "behind", "struggling",
            "not productive", "unproductive", "can't finish", "cannot finish",
        ]):
            facts["productivity"] = {"task_completion": "Poor"}
        elif _has_any(productivity_context, ["productive", "efficient", "get things done", "on top of"]):
            facts["productivity"] = {"task_completion": "Good"}
        else:
            facts["productivity"] = {"task_completion": "Fair"}

    # -------------------------
    # Time Management
    # -------------------------
    time_context = _latest_context(sentences, [
        "schedule", "scheduling", "plan", "planning", "organized",
        "organised", "disorganized", "disorganised", "deadline", "last minute",
        "time management",
    ])

    if time_context:
        if _has_any(time_context, [
            "no schedule", "can't manage", "cannot manage", "always late",
            "disorganized", "disorganised", "last minute", "no plan",
            "don't plan", "do not plan", "don't schedule", "do not schedule",
            "bad at time",
        ]):
            facts["time_management"] = {"planning": "Poor"}
        elif _has_any(time_context, ["plan", "schedule", "organized", "organised", "calendar"]):
            facts["time_management"] = {"planning": "Good"}
        else:
            facts["time_management"] = {"planning": "Fair"}

    # -------------------------
    # Social Support
    # -------------------------
    social_context = _latest_context(sentences, [
        "friend", "friends", "family", "social", "alone", "lonely", "support",
        "talk to", "people",
    ])

    if social_context:
        if _has_any(social_context, [
            "alone", "no one", "no friends", "don't have", "do not have",
            "isolated", "lonely", "nobody",
        ]):
            facts["social_support"] = {"support_availability": "Low"}
        elif _has_any(social_context, ["friends", "family", "support", "talk to", "people", "someone"]):
            facts["social_support"] = {"support_availability": "Available"}
        elif _has_any(social_context, ["sometimes", "a few"]):
            facts["social_support"] = {"support_availability": "Sometimes"}

    # -------------------------
    # Lifestyle
    # -------------------------
    lifestyle_context = _latest_context(sentences, [
        "routine", "meal", "meals", "eat", "eating", "water", "hydrated",
        "diet", "lifestyle", "sleep schedule",
    ])

    if lifestyle_context:
        if _has_any(lifestyle_context, [
            "no routine", "bad", "irregular", "unhealthy", "skip meals",
            "don't eat", "do not eat", "not eating",
        ]):
            facts["lifestyle"] = {"daily_routine": "Poor"}
        elif _has_any(lifestyle_context, ["regular", "healthy", "balanced", "good"]):
            facts["lifestyle"] = {"daily_routine": "Good"}
        else:
            facts["lifestyle"] = {"daily_routine": "Fair"}

    # -------------------------
    # Digital Behaviour
    # -------------------------
    digital_context = _latest_context(sentences, [
        "phone", "screen", "social media", "scrolling", "scroll", "gaming",
        "games", "digital", "instagram", "tiktok", "youtube", "doomscroll",
    ])

    if digital_context:
        if _has_any(digital_context, [
            "can't control", "cannot control", "too much", "addicted", "excessive",
            "all night", "doomscroll", "constantly",
        ]):
            facts["digital_behaviour"] = {"screen_time_control": "Poor"}
        elif _has_any(digital_context, ["limit", "manage", "control", "balanced"]):
            facts["digital_behaviour"] = {"screen_time_control": "Good"}
        else:
            facts["digital_behaviour"] = {"screen_time_control": "Fair"}

    # -------------------------
    # Recent Life Events
    # -------------------------
    life_context = _latest_context(sentences, [
        "major change", "big change", "moved", "moving", "breakup", "broke up",
        "lost someone", "passed away", "bereavement", "family issue",
        "health problem", "trauma", "new school", "changed schools",
    ])

    if life_context:
        if _has_any(life_context, ["nothing major", "no major change", "no changes", "none", "nothing", "not really"]):
            facts["recent_life_events"] = {"major_changes": "None"}
        elif _has_any(life_context, ["major", "big", "significant", "traumatic", "lost someone", "passed away", "breakup", "broke up"]):
            facts["recent_life_events"] = {"major_changes": "Major"}
        else:
            facts["recent_life_events"] = {"major_changes": "Minor"}

    # -------------------------
    # Personality Traits
    # -------------------------
    perfectionism_context = _latest_context(sentences, [
        "perfectionist", "perfectionism", "perfect", "high standards",
        "never good enough", "not good enough",
    ])

    if perfectionism_context:
        if _has_any(perfectionism_context, ["not a perfectionist", "no", "low"]):
            facts["personality_traits"] = {"perfectionism_pressure": "Low"}
        else:
            facts["personality_traits"] = {"perfectionism_pressure": "High"}

    # -------------------------
    # Exercise
    # -------------------------
    exercise_context = _latest_context(sentences, [
        "exercise", "walk", "walking", "run", "running", "gym", "sport",
        "sports", "physical", "yoga", "workout", "work out", "active",
    ])

    if exercise_context:
        if _has_any(exercise_context, ["no exercise", "never", "don't exercise", "do not exercise", "sedentary"]):
            facts["exercise"] = {"physical_activity": "Never"}
        elif _has_any(exercise_context, ["rarely", "not much"]):
            facts["exercise"] = {"physical_activity": "Rarely"}
        elif _has_any(exercise_context, ["sometimes", "occasionally"]):
            facts["exercise"] = {"physical_activity": "Sometimes"}
        elif _has_any(exercise_context, ["regular", "daily", "every day", "often", "gym", "workout", "work out"]):
            facts["exercise"] = {"physical_activity": "Regular"}
        else:
            facts["exercise"] = {"physical_activity": "Sometimes"}

    return facts


def clean_json(output):
    try:
        import json
        return json.loads(output)
    except (json.JSONDecodeError, TypeError):
        return {}
