import re


def extract_facts(text: str):
    facts = {}
    text_lower = text.lower()

    # -------------------------
    # Sleep
    # -------------------------
    if "sleep" in text_lower or "tired" in text_lower or "rest" in text_lower:
        sleep = {}

        hours_match = re.search(r"(\d+)\s*[-–to]*\s*(\d*)\s*hour", text_lower)
        if hours_match:
            try:
                val = int(hours_match.group(1))
                sleep["hours"] = max(3, min(10, val))
            except (ValueError, IndexError):
                pass

        if not sleep.get("hours"):
            single_match = re.search(r"about\s*(\d+)\s*hour", text_lower) or \
                           re.search(r"only\s*(\d+)\s*hour", text_lower) or \
                           re.search(r"(\d+)\s*hr", text_lower)
            if single_match:
                try:
                    sleep["hours"] = max(3, min(10, int(single_match.group(1))))
                except ValueError:
                    pass

        if any(w in text_lower for w in ["poor", "bad", "terrible", "awful", "not good"]):
            sleep["quality"] = "Poor"
        elif any(w in text_lower for w in ["good", "decent", "okay", "fair"]):
            sleep["quality"] = "Fair"

        if "tired" in text_lower or "exhausted" in text_lower or "drained" in text_lower:
            sleep["rested"] = "Rarely"

        if "irregular" in text_lower or "inconsistent" in text_lower or "can't sleep" in text_lower:
            sleep["consistency"] = "Irregular"

        if sleep:
            facts["sleep"] = sleep

    # -------------------------
    # Academic Load
    # -------------------------
    if any(w in text_lower for w in ["study", "exam", "assignment", "homework", "class", "school", "academic", "grade", "project"]):
        acad = {}

        hours_match = re.search(r"(\d+)\s*hour.*(?:study|work|class)", text_lower)
        if hours_match:
            try:
                acad["study_hours"] = max(0, min(16, int(hours_match.group(1))))
            except ValueError:
                pass

        if any(w in text_lower for w in ["overwhelming", "too much", "heavy", "excessive", "a lot"]):
            acad["homework_load"] = "Heavy"
        elif any(w in text_lower for w in ["moderate", "okay", "manageable"]):
            acad["homework_load"] = "Moderate"
        else:
            acad["homework_load"] = "Moderate"

        if any(w in text_lower for w in ["exam", "test", "assessment"]):
            acad["upcoming_exams"] = "Yes"
            acad["assignments"] = "Several"

        if facts.get("sleep") and facts["sleep"].get("hours", 7) < 6:
            acad["attendance"] = 80
        else:
            acad["attendance"] = 90

        if acad:
            facts["academic_load"] = acad

    # -------------------------
    # Emotional Exhaustion
    # -------------------------
    if any(w in text_lower for w in ["drained", "exhausted", "burnout", "overwhelmed", "can't cope", "emotionally"]):
        facts["emotional_exhaustion"] = {
            "feeling_drained": "Often" if any(w in text_lower for w in ["drained", "exhausted", "overwhelmed"]) else "Sometimes",
            "recovery_after_rest": "Rarely" if "tired" in text_lower else "Sometimes",
        }

    # -------------------------
    # Burnout Symptoms
    # -------------------------
    if any(w in text_lower for w in ["overwhelmed", "burnout", "can't do this", "giving up", "hopeless"]):
        facts["burnout_symptoms"] = {
            "overwhelmed": "Often" if "overwhelmed" in text_lower else "Sometimes",
            "loss_of_interest": "Sometimes" if "don't care" in text_lower or "not interested" in text_lower else "Rarely",
        }

    # -------------------------
    # Motivation
    # -------------------------
    if any(w in text_lower for w in ["motivat", "procrastinat", "can't start", "don't feel like"]):
        facts["motivation"] = {
            "study_motivation": "Low" if any(w in text_lower for w in ["no motivation", "low", "struggling", "can't"]) else "Moderate"
        }

    # -------------------------
    # Cognitive
    # -------------------------
    if any(w in text_lower for w in ["concentrat", "focus", "memory", "brain fog", "forget"]):
        facts["cognitive"] = {
            "concentration": "Low" if any(w in text_lower for w in ["can't focus", "difficult", "poor", "bad"]) else "Moderate",
            "memory": "Low" if "memory" in text_lower else "Moderate",
        }

    # -------------------------
    # Stress
    # -------------------------
    if any(w in text_lower for w in ["stress", "pressure", "worried", "anxious"]):
        stress_freq = "High"
        if "low" in text_lower:
            stress_freq = "Low"
        elif "moderate" in text_lower or "okay" in text_lower:
            stress_freq = "Moderate"
        facts["stress"] = {
            "stress_frequency": stress_freq,
            "stress_control": "Low" if any(w in text_lower for w in ["can't control", "overwhelming", "too much"]) else "Moderate",
        }

    # -------------------------
    # Anxiety
    # -------------------------
    if any(w in text_lower for w in ["anxious", "worry", "nervous", "fear", "panic"]):
        facts["anxiety"] = {
            "worry_frequency": "Often" if any(w in text_lower for w in ["always", "constantly", "every day"]) else "Sometimes"
        }

    # -------------------------
    # Mood
    # -------------------------
    if any(w in text_lower for w in ["mood", "sad", "happy", "down", "low", "depressed", "irritable"]):
        mood_state = "Low" if any(w in text_lower for w in ["sad", "down", "low", "depressed", "irritable"]) else "Moderate"
        facts["mood"] = {
            "positive_mood": mood_state
        }

    # -------------------------
    # Productivity
    # -------------------------
    if any(w in text_lower for w in ["productiv", "task", "deadline", "work", "efficient"]):
        facts["productivity"] = {
            "task_completion": "Low" if any(w in text_lower for w in ["can't complete", "behind", "struggling", "lazy"]) else "Moderate",
        }

    # -------------------------
    # Time Management
    # -------------------------
    if any(w in text_lower for w in ["time", "schedule", "plan", "organize", "deadline"]):
        facts["time_management"] = {
            "planning": "Poor" if any(w in text_lower for w in ["no time", "can't manage", "always late", "bad"]) else "Fair"
        }

    # -------------------------
    # Social Support
    # -------------------------
    if any(w in text_lower for w in ["friend", "family", "social", "alone", "support", "talk", "people"]):
        facts["social_support"] = {
            "support_availability": "Low" if any(w in text_lower for w in ["alone", "no one", "don't have", "isolated"]) else "Available"
        }

    # -------------------------
    # Lifestyle
    # -------------------------
    if any(w in text_lower for w in ["routine", "meal", "eat", "water", "diet", "lifestyle"]):
        facts["lifestyle"] = {
            "daily_routine": "Poor" if any(w in text_lower for w in ["no routine", "bad", "irregular", "unhealthy"]) else "Fair"
        }

    # -------------------------
    # Digital Behaviour
    # -------------------------
    if any(w in text_lower for w in ["phone", "screen", "social media", "scrolling", "gaming", "digital"]):
        facts["digital_behaviour"] = {
            "screen_time_control": "Poor" if any(w in text_lower for w in ["can't control", "too much", "addicted", "excessive"]) else "Moderate"
        }

    # -------------------------
    # Recent Life Events
    # -------------------------
    if any(w in text_lower for w in ["change", "move", "lost", "breakup", "family issue", "health problem", "trauma"]):
        facts["recent_life_events"] = {
            "major_changes": "Yes" if any(w in text_lower for w in ["major", "big", "significant", "traumatic"]) else "Minor"
        }

    # -------------------------
    # Exercise
    # -------------------------
    if any(w in text_lower for w in ["exercise", "walk", "run", "gym", "sport", "physical", "yoga", "workout"]):
        facts["exercise"] = {
            "physical_activity": "Low" if any(w in text_lower for w in ["no", "don't", "never", "rarely"]) else "Regular"
        }

    return facts


def clean_json(output):
    try:
        import json
        return json.loads(output)
    except (json.JSONDecodeError, TypeError):
        return {}
