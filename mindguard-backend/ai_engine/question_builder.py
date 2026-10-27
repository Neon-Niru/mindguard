from .state_manager import get_missing_fields, REQUIRED_INTERVIEW_CATEGORIES


CATEGORY_NAMES = {
    "sleep": "your sleep",
    "academic_load": "your school workload",
    "emotional_exhaustion": "how emotionally drained you feel",
    "burnout_symptoms": "feeling overwhelmed or losing interest",
    "motivation": "your study motivation",
    "cognitive": "concentration and memory",
    "stress": "stress",
    "anxiety": "worry",
    "mood": "your mood",
    "productivity": "getting tasks done",
    "time_management": "managing your time",
    "recent_life_events": "recent life changes",
    "personality_traits": "pressure you put on yourself",
    "digital_behaviour": "your screen habits",
    "lifestyle": "your daily routine",
    "social_support": "support from people around you",
    "exercise": "physical activity",
}

FIELD_PHRASES = {
    ("sleep", "hours"): "about how many hours you sleep on a typical night",
    ("sleep", "quality"): "how you would describe the quality of your sleep",
    ("sleep", "rested"): "whether you usually wake feeling rested",
    ("sleep", "consistency"): "whether your sleep schedule is regular or varies",
    ("academic_load", "study_hours"): "about how many hours you study in a typical week",
    ("academic_load", "homework_load"): "how heavy your homework load feels",
    ("academic_load", "assignments"): "how many assignments you usually have at once",
    ("academic_load", "projects"): "how often you have projects to work on",
    ("academic_load", "upcoming_exams"): "whether you have exams coming up",
    ("academic_load", "subject_difficulty"): "how difficult your subjects feel",
    ("academic_load", "academic_expectations"): "how much pressure you feel from academic expectations",
    ("academic_load", "attendance"): "roughly what percentage of classes you attend",
    ("emotional_exhaustion", "feeling_drained"): "how often you feel emotionally drained",
    ("emotional_exhaustion", "recovery_after_rest"): "whether rest helps you recover",
    ("burnout_symptoms", "overwhelmed"): "how often you feel overwhelmed",
    ("burnout_symptoms", "loss_of_interest"): "whether you have lost interest in things you usually enjoy",
    ("motivation", "study_motivation"): "how your motivation to study has been",
    ("cognitive", "concentration"): "how well you can concentrate",
    ("cognitive", "memory"): "how your memory has been",
    ("stress", "stress_frequency"): "how often you feel stressed",
    ("stress", "stress_control"): "how manageable that stress feels",
    ("anxiety", "worry_frequency"): "how often you find yourself worrying",
    ("mood", "positive_mood"): "how your mood has generally been",
    ("productivity", "task_completion"): "how often you complete the tasks you plan to do",
    ("time_management", "planning"): "how well your plans and schedule are working",
    ("recent_life_events", "major_changes"): "whether any significant changes have happened recently",
    ("personality_traits", "perfectionism_pressure"): "how much pressure you put on yourself to get things exactly right",
    ("digital_behaviour", "screen_time_control"): "how in control you feel of your screen time",
    ("lifestyle", "daily_routine"): "how regular and supportive your daily routine feels",
    ("social_support", "support_availability"): "whether you have someone you can talk to for support",
    ("exercise", "physical_activity"): "how often you get physical activity",
}

REPHRASED_SINGLE_QUESTIONS = {
    ("sleep", "hours"): "About how many hours is a typical night's sleep for you?",
    ("sleep", "quality"): "What words best describe the quality of your sleep?",
    ("sleep", "rested"): "When you wake up, do you usually feel rested?",
    ("sleep", "consistency"): "Does your sleep schedule stay fairly regular, or does it vary?",
}


def collected_field_keys(state):
    return {
        (category, field)
        for category, values in state.get("data", {}).items()
        if isinstance(values, dict)
        for field, value in values.items()
        if value is not None
    }


def _choose_category(missing, previous_asked, made_progress):
    missing_categories = list(dict.fromkeys(item["category"] for item in missing))
    order = REQUIRED_INTERVIEW_CATEGORIES

    # If the person did not answer the current topic, clarify it once instead
    # of abruptly switching subjects.
    if not made_progress and previous_asked:
        current_category = next(
            (category for category in order
             if any(key[0] == category for key in previous_asked)),
            None,
        )
        if current_category in missing_categories:
            return current_category

    last_index = max(
        (index for index, category in enumerate(order)
         if any(key[0] == category for key in previous_asked)),
        default=-1,
    )
    for offset in range(1, len(order) + 1):
        category = order[(last_index + offset) % len(order)]
        if category in missing_categories:
            return category

    return missing_categories[0]


def build_followup_question(state, previous_asked=(), made_progress=True):
    missing = get_missing_fields(state)
    if not missing:
        return "", []

    category = _choose_category(missing, previous_asked, made_progress)
    requested = [item for item in missing if item["category"] == category][:4]
    keys = [(item["category"], item["field"]) for item in requested]
    labels = [FIELD_PHRASES.get(key, key[1].replace("_", " ")) for key in keys]
    category_name = CATEGORY_NAMES.get(category, category.replace("_", " "))

    if not made_progress and any(key in set(previous_asked) for key in keys):
        first_key = keys[0]
        question = REPHRASED_SINGLE_QUESTIONS.get(first_key)
        if question is None:
            question = f"Could you say a little more about {labels[0]}?"
        return "Sorry, I may have asked that unclearly. " + question, [first_key]

    if len(labels) == 1:
        question = f"Could you share {labels[0]}?"
    else:
        joined = ", ".join(labels[:-1]) + f", and {labels[-1]}"
        question = f"To understand {category_name}, could you share {joined}?"

    return question, keys
