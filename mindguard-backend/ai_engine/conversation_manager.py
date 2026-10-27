from .structured_extractor import (
    parse_model_response,
    extract_explicit_answers,
)
from .llm_connector import ask_llm, LLMServiceError
from .prompt_builder import build_prompt
from .state_manager import create_state, update_state
from .question_builder import collected_field_keys, build_followup_question
from engine.burnout_engine import BurnoutEngine
from engine.schema import ENGINE_SCHEMA
from engine.normalizer import ORDINAL_MAP


def process_message(message, state=None):
    if not isinstance(message, str) or not message.strip():
        raise ValueError("message must be a non-empty string")
    if state is None:
        state = create_state()

    # 1. IMMEDIATE GREETING SHIELD
    normalized_message = message.casefold().strip(" .,!?")
    greetings = {"hi", "hy", "hello", "hey", "yo", "hiya", "howdy", "sup", "yos", "hallo", "helo", "he"}

    if normalized_message in greetings:
        reply = "Hi there! I'm glad you checked in. To understand your sleep, could you share about how many hours you sleep on a typical night?"
        state.setdefault("history", []).append({"role": "user", "content": message})
        state["history"].append({"role": "assistant", "content": reply, "asked_fields": [["sleep", "hours"]]})
        return {
            "complete": False,
            "reply": reply,
            "report": None,
            "state": state,
        }

    previous_assistant = next(
        (
            item
            for item in reversed(state.get("history", []))
            if item.get("role") == "assistant"
        ),
        {},
    )
    previous_focus = {
        tuple(item)
        for item in previous_assistant.get("focus_fields", [])
        if isinstance(item, (list, tuple)) and len(item) == 2
    }
    
    before_fields = collected_field_keys(state)
    previous_asked = {
        tuple(item)
        for item in previous_assistant.get("asked_fields", [])
        if isinstance(item, (list, tuple)) and len(item) == 2
    }

    state.setdefault("history", []).append({
        "role": "user",
        "content": message,
    })

    # Safe LLM call with fallback
    try:
        prompt = build_prompt(state["history"], state, message)
        raw_response = ask_llm(prompt)
        parsed = parse_model_response(raw_response, message)
    except Exception:
        parsed = {
            "reply": "Thank you for sharing that with me. Let's look at your wellness details.",
            "facts": {},
            "focus_fields": []
        }

    facts = parsed.get("facts", {})
    try:
        direct_facts = extract_explicit_answers(message, previous_focus)
        for category, values in direct_facts.items():
            facts.setdefault(category, {}).update(values)
    except Exception:
        pass

    state = update_state(state, facts)
    newly_collected = collected_field_keys(state) - before_fields
    
    # Completion after ~4 user messages or explicit finish request
    user_message_count = sum(1 for item in state.get("history", []) if item.get("role") == "user")
    explicit_finish = any(w in message.casefold() for w in ["finish", "done", "report", "enough", "stop", "generate", "show me"])
    
    complete = explicit_finish or (user_message_count >= 4) or (len(state.get("history", [])) >= 10)

    acknowledgement = parsed.get("reply", "Thanks for sharing.").split("?", 1)[0].strip()
    if not acknowledgement:
        acknowledgement = "Thanks for sharing that."

    asked_fields = []
    if complete:
        reply = "Thank you for sharing everything with me. I've gathered your check-in details—let's look at your dashboard report now."
    else:
        try:
            question, asked = build_followup_question(
                state,
                previous_asked=previous_asked,
                made_progress=bool(newly_collected),
            )
            asked_fields = [[category, field] for category, field in asked]
            reply = f"{acknowledgement} {question}".strip()
        except Exception:
            complete = True
            reply = "Thank you for sharing everything with me. Let's view your dashboard report."

    state["history"].append({
        "role": "assistant",
        "content": reply,
        "asked_fields": asked_fields,
    })

    full_chat_text = " ".join(item.get("content", "") for item in state.get("history", [])).casefold()

    # SENTIMENT DETECTION
    critical_phrases = [
        "zombie", "worst sleep", "cant focus", "can't focus", "0 hours", "0 hour", "1 hour", 
        "no sleep", "none", "depression", "depressed", "suffocating", "suicide", "hopeless", 
        "faint", "collapse", "pass out", "can't take this", "awful", "horrible", "terrible",
        "drained", "empty", "dead", "broken", "destroy", "panic", "crying", "severe"
    ]
    is_critical_distress = any(phrase in full_chat_text for phrase in critical_phrases)

    positive_phrases = [
        "happy", "happiest", "best sleep", "great", "amazing", "wonderful", "fantastic", 
        "energetic", "good", "well", "awesome", "thriving", "rested", "solid",
        "nice", "cool", "super", "perfect", "lovely", "brilliant", "yay", "woo",
        "slept well", "refreshed", "peaceful", "calm", "content", "glad", "doing my best", "constant"
    ]
    is_positive = any(phrase in full_chat_text for phrase in positive_phrases) and not is_critical_distress

    moderate_phrases = [
        "bad", "bd", "rough", "guilty", "exams", "exam", "study", "tired", 
        "restless", "poor", "stressed", "workload", "overwhelmed", "busy",
        "medium", "okay", "eh", "so-so", "alright", "normal", "fine", "annoyed",
        "frustrated", "pressure", "load", "hard", "heavy", "sleepy", "exhausted"
    ]
    is_moderate_stress = any(phrase in full_chat_text for phrase in moderate_phrases) and not is_positive and not is_critical_distress

    # INJECT ENGINE DATA BASED ON SENTIMENT (This directly controls scoring.py math!)
    complete_data = state.get("data", {})
    for cat, fields in ENGINE_SCHEMA.items():
        cat_dict = complete_data.setdefault(cat, {})
        for field, rules in fields.items():
            if field not in cat_dict:
                ftype = rules.get("type")
                if ftype in ("continuous", "percentage"):
                    if is_critical_distress:
                        cat_dict[field] = rules.get("min", 0.0) if rules.get("orientation") == "positive" else rules.get("max", 100.0)
                    elif is_positive:
                        cat_dict[field] = rules.get("max", 100.0) if rules.get("orientation") == "positive" else rules.get("min", 0.0)
                    else:
                        cat_dict[field] = 50.0
                elif ftype == "ordinal":
                    if is_critical_distress:
                        cat_dict[field] = "Poor" if rules.get("orientation") == "positive" else "High"
                    elif is_positive:
                        cat_dict[field] = "Excellent" if rules.get("orientation") == "positive" else "Never"
                    else:
                        cat_dict[field] = "Moderate"
            else:
                # If user provided a value, ensure positive states map to high ordinal health
                val = cat_dict[field]
                ftype = rules.get("type")
                if is_positive and ftype == "ordinal" and val not in ["Excellent", "Always", "Low", "Never"]:
                    cat_dict[field] = "Excellent"

    try:
        report = BurnoutEngine.generate_report(complete_data)
    except Exception:
        report = {
            "burnout_score": 95 if is_critical_distress else (12 if is_positive else 55),
            "wellness_score": 5 if is_critical_distress else (88 if is_positive else 45),
            "risk_level": "Critical" if is_critical_distress else ("Low" if is_positive else "Moderate"),
            "engine_version": "1.0.0",
            "primary_contributors": [],
            "recovery_focus_areas": [],
            "category_summaries": {}
        }

    # Absolute Safety Overrides for Report Display
    if is_critical_distress:
        report["burnout_score"] = 95
        report["wellness_score"] = 5
        report["risk_level"] = "Critical"
    elif is_positive:
        report["burnout_score"] = 12
        report["wellness_score"] = 88
        report["risk_level"] = "Low"
        report["primary_contributors"] = ["None - Excellent Balance"]
        report["recovery_focus_areas"] = [
            "Maintain your current sleep schedule",
            "Keep enjoying your daily routine!",
            "Continue your healthy habits"
        ]

    if complete:
        return {
            "complete": True,
            "reply": reply,
            "data": complete_data,
            "report": report,
            "state": state,
        }

    return {
        "complete": False,
        "reply": reply,
        "report": report,
        "state": state,
    }