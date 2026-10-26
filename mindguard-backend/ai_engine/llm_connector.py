import os
import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def _build_hf_prompt(messages):
    system_parts = []
    user_message = ""
    for msg in messages:
        if msg["role"] == "system":
            system_parts.append(msg["content"])
        elif msg["role"] == "user":
            user_message = msg["content"]
    system_text = "\n\n".join(system_parts)
    return f"<s>[INST] {system_text}\n\n{user_message} [/INST]"


def ask_llm(messages, state=None):
    provider = os.getenv("LLM_PROVIDER", "groq").lower()
    api_key = os.getenv(f"{provider.upper()}_API_KEY")

    # Hugging Face Inference API
    if provider in ("hf", "huggingface"):
        if not api_key:
            # No key: let the conversation manager use the deterministic
            # interviewer, which rotates topics and never repeats a question.
            return None

        model = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")
        api_url = f"https://api-inference.huggingface.co/models/{model}"

        prompt = _build_hf_prompt(messages)
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.8,
                "return_full_text": False,
            },
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
        except requests.RequestException as error:
            raise Exception(f"LLM request failed: {error}")

        data = response.json()
        try:
            return data[0][0]["generated_text"]
        except (KeyError, IndexError, TypeError):
            raise Exception("Invalid LLM response format")

    if not api_key:
        # No key: the conversation manager falls back to the deterministic
        # interviewer instead of a fixed question.
        return None

    if provider == "openrouter":
        api_url = os.getenv("OPENROUTER_URL", DEFAULT_OPENROUTER_URL)
        model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct")
    else:
        api_url = os.getenv("GROQ_URL", DEFAULT_GROQ_URL)
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.8,
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
