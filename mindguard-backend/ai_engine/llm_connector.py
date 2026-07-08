import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

_FALLBACK_QUESTIONS = [
    "How has your week been going?",
    "Tell me about your sleep lately.",
    "How are you feeling emotionally?",
    "How is your academic workload?",
    "Have you been feeling motivated?",
    "How is your concentration?",
    "How would you describe your stress level?",
    "How are you managing your time?",
    "Do you feel supported by those around you?",
    "Tell me about your daily routine.",
]


def ask_llm(messages, state=None):
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    api_key = os.getenv(f"{provider.upper()}_API_KEY")

    if not api_key:
        if state and state.get("missing"):
            cat = state["missing"][0]
            questions = {
                "sleep": "How has your sleep been this week?",
                "academic_load": "How are your studies going?",
                "emotional_exhaustion": "Have you been feeling emotionally drained?",
                "motivation": "How is your motivation for studying these days?",
                "cognitive": "How is your concentration and memory?",
                "stress": "How would you rate your stress level?",
                "anxiety": "Do you find yourself worrying often?",
                "mood": "How has your mood been lately?",
                "productivity": "How productive have you been feeling?",
                "time_management": "How well are you managing your time?",
                "social_support": "Do you have people you can talk to?",
                "lifestyle": "How is your daily routine?",
                "digital_behaviour": "How is your screen time?",
                "burnout_symptoms": "Have you been feeling overwhelmed?",
                "recent_life_events": "Have there been any major changes recently?",
                "exercise": "Are you getting any physical activity?",
            }
            return questions.get(cat, "Tell me more about how you've been feeling.")
        return "Thank you for sharing. I think I have enough information now."

    if provider == "openrouter":
        api_url = os.getenv("OPENROUTER_URL", DEFAULT_OPENROUTER_URL)
        model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
    else:
        api_url = os.getenv("GROQ_URL", DEFAULT_GROQ_URL)
        model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        raise Exception(f"LLM request failed: {error}")

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        raise Exception("Invalid LLM response format")
