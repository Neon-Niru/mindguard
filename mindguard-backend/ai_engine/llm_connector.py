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


class LLMServiceError(RuntimeError):
    """A safe, user-facing error from the configured language-model service."""


def ask_llm(messages):
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()
    if provider not in {"groq", "openrouter"}:
        raise LLMServiceError("Unsupported LLM_PROVIDER; use 'groq' or 'openrouter'.")
    api_key = os.getenv(f"{provider.upper()}_API_KEY")

    if not api_key:
        raise LLMServiceError(f"{provider.upper()}_API_KEY is not configured.")

    if provider == "openrouter":
        api_url = os.getenv("OPENROUTER_URL", DEFAULT_OPENROUTER_URL)
        model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
    else:
        api_url = os.getenv("GROQ_URL", DEFAULT_GROQ_URL)
        model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    payload = {
        "model": model,
        "messages": messages,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise LLMServiceError("AI provider returned an empty response.")
        return content
    except LLMServiceError:
        raise
    except requests.RequestException as error:
        status = getattr(getattr(error, "response", None), "status_code", None)
        if status:
            raise LLMServiceError(f"LLM provider request failed (HTTP {status}).") from error
        raise LLMServiceError("Could not reach the LLM provider.") from error
    except (KeyError, IndexError, TypeError, ValueError) as error:
        raise LLMServiceError("LLM provider returned an invalid response.") from error