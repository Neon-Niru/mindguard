"""Deterministic interviewer used when no LLM is configured or reachable.

The LLM is only the conversational layer. When it is unavailable the app still
has to run a coherent interview, so this module picks the next topic, varies
its phrasing, and never repeats the same question twice in a row.

It does not score anything and does not invent facts: the extractor (with the
topic of the question just asked) decides what was actually reported.
"""

import re

from .state_manager import REQUIRED_INTERVIEW_CATEGORIES


# Two phrasings per category: an open one, then a concrete one that offers
# labels/numbers the extractor can understand. A student can answer tersely
# ("heavy", "5 hours", "ok") and the answer is still usable.
QUESTION_VARIANTS = {
    "academic_load": [
        "How heavy is your study load right now — light, manageable, or heavy?",
        "Roughly how many hours a day do you spend on classes, homework, and revision?",
    ],
    "sleep": [
        "How is your sleep at the moment — how many hours, and how well do you sleep?",
        "Do you wake up feeling rested, and is your bedtime roughly the same each night?",
    ],
    "stress": [
        "How would you describe your stress level right now — low, moderate, or high?",
        "Do you feel like you can manage the pressure, or does it feel out of control?",
    ],
    "motivation": [
        "How is your motivation for studying these days — good, up and down, or low?",
        "Do you find yourself procrastinating, or can you start tasks fairly easily?",
    ],
    "mood": [
        "How has your mood been this week — good, okay, or low?",
        "Have you felt down, irritable, or mostly steady?",
    ],
    "cognitive": [
        "How is your concentration when you sit down to study — good, fair, or poor?",
        "Do you find yourself distracted or forgetting things more than usual?",
    ],
    "lifestyle": [
        "How is your daily routine — meals, water, and your sleep schedule?",
        "Are meals and rest fairly regular, or do they slip when things get busy?",
    ],
    "time_management": [
        "How are you managing your time — do you plan ahead, or is it more last minute?",
        "Do you keep a schedule, or do deadlines tend to pile up?",
    ],
    "social_support": [
        "Do you have people you can talk to when things get hard — friends, family, someone?",
        "When you're stressed, is there someone you can lean on, or do you handle it alone?",
    ],
    "digital_behaviour": [
        "How is your screen time — do you feel in control of it, or does it take over?",
        "Do phone or social media habits cut into your sleep or study time?",
    ],
    "recent_life_events": [
        "Has anything major changed recently — school, family, relationships, health?",
        "Any big changes or difficult events in the last few months?",
    ],
    "emotional_exhaustion": [
        "Have you been feeling emotionally drained — often, sometimes, or rarely?",
        "After you rest, do you feel recovered, or still tired?",
    ],
    "burnout_symptoms": [
        "Have you been feeling overwhelmed, or like you're losing interest in things?",
        "Does it ever feel like too much to keep up with?",
    ],
    "anxiety": [
        "Do you find yourself worrying — often, sometimes, or rarely?",
        "Do worries keep you up at night or distract you during the day?",
    ],
    "productivity": [
        "How productive have you been feeling — on top of things, or falling behind?",
        "Are you getting tasks done, or do they keep slipping?",
    ],
    "exercise": [
        "Are you getting any physical activity — walking, sport, gym, anything?",
        "How often do you move your body in a normal week — daily, sometimes, or rarely?",
    ],
}

# Why each topic is asked. Used to answer "why are you asking that again?".
CATEGORY_REASONS = {
    "academic_load": "how much pressure your workload is putting on you",
    "sleep": "sleep is one of the earliest signals that things are getting heavy",
    "stress": "how much pressure you're carrying right now",
    "motivation": "whether your energy for studying is holding up",
    "mood": "how you've been feeling day to day",
    "cognitive": "whether stress is starting to affect your focus",
    "lifestyle": "whether the basics like meals and rest are steady",
    "time_management": "how much of the pressure comes from planning",
    "social_support": "whether you have people to lean on",
    "digital_behaviour": "whether screens are eating into rest or study time",
    "recent_life_events": "whether something recent is adding to the load",
    "emotional_exhaustion": "how tired you are underneath the busyness",
    "burnout_symptoms": "the clearest early signs of burnout",
    "anxiety": "how much worry is running in the background",
    "productivity": "how work is actually going day to day",
    "exercise": "movement is one of the strongest recovery factors",
}

DEFAULT_QUESTION = "Tell me a little more about how things have been for you."

# After this many attempts a topic is pushed to the back of the queue so the
# conversation keeps moving even when the student would rather skip it.
MAX_PROBES_PER_CATEGORY = 3

_TOPIC_BY_QUESTION = {
    question: category
    for category, variants in QUESTION_VARIANTS.items()
    for question in variants
}


def topic_for_question(text):
    """Return the category a known question belongs to, if any."""
    if not isinstance(text, str):
        return None
    return _TOPIC_BY_QUESTION.get(text.strip())


def derive_progress(history):
    """Reconstruct question rotation state from stored conversation history.

    Keeping this derivable means no schema change is needed: the transcript in
    the session row is the source of truth.
    """
    asked = {}
    last_question = ""
    last_topic = None

    for item in history or []:
        if item.get("role") != "assistant":
            continue

        content = (item.get("content") or "").strip()
        category = _TOPIC_BY_QUESTION.get(content)

        if category:
            asked[category] = asked.get(category, 0) + 1
            last_question = content
            last_topic = category

    return asked, last_question, last_topic


def _order(category):
    return REQUIRED_INTERVIEW_CATEGORIES.index(category)


def next_question(state, prefer=None):
    """Choose the next thing to ask and remember that we asked it.

    ``prefer`` keeps the conversation on a topic that is still missing (used
    when the student asks what we mean instead of answering).
    """
    missing = [
        category for category in REQUIRED_INTERVIEW_CATEGORIES
        if category in (state.get("missing") or [])
    ]

    if not missing:
        return None

    asked = state.setdefault("asked", {})
    last_question = state.get("last_question") or ""

    # Stay on the topic the student just questioned, but only while it has not
    # been probed too often — otherwise a confused student would be stuck.
    if prefer in missing and asked.get(prefer, 0) < MAX_PROBES_PER_CATEGORY:
        category = prefer
    else:
        # Least-asked topic first, then the interview's canonical order. This
        # is what stops the same question repeating when an answer is too
        # vague to extract: the topic moves on and can be revisited later.
        category = min(
            missing,
            key=lambda cat: (asked.get(cat, 0), _order(cat)),
        )

    variants = QUESTION_VARIANTS.get(category) or [DEFAULT_QUESTION]
    attempts = asked.get(category, 0)
    text = variants[min(attempts, len(variants) - 1)]

    if text == last_question:
        text = variants[(min(attempts, len(variants) - 1) + 1) % len(variants)]

    asked[category] = attempts + 1
    state["last_question"] = text
    state["last_topic"] = category

    return text


CONFUSION_MARKERS = (
    "huh",
    "idk",
    "i don't know",
    "i dont know",
    "dunno",
    "not sure",
    "no idea",
    "what do you mean",
    "why",
    "again",
    "repeat",
)

_CONFUSION_PATTERN = re.compile(
    r"(?<![a-z])("
    + "|".join(
        re.escape(marker)
        for marker in sorted(CONFUSION_MARKERS, key=len, reverse=True)
    )
    + r")(?![a-z])"
)


def looks_confused(message):
    """True when the student is asking what we mean rather than answering."""
    text = (message or "").strip().lower()

    if not text:
        return False

    # A question mark is a strong signal; the markers cover statements like
    # "huh" or "I don't know" that do not bother with punctuation.
    if "?" in text:
        return True

    return bool(_CONFUSION_PATTERN.search(text))


def explain(category):
    reason = CATEGORY_REASONS.get(category)
    if not reason:
        return "I'm just trying to get a clearer picture of your week."
    return f"That one helps me understand {reason}."
