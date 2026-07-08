"""
MindGuard AI

LLM Connector

Responsibility:

Only communicates with external LLM providers.

Supports:
- Groq
- OpenRouter

Does NOT:
- build prompts
- manage conversation
- extract facts
- calculate burnout
"""


import os
import requests

from dotenv import load_dotenv


load_dotenv()



DEFAULT_GROQ_URL = (
    "https://api.groq.com/openai/v1/chat/completions"
)


DEFAULT_OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)




def ask_llm(messages):


    provider = os.getenv(
        "LLM_PROVIDER",
        "groq"
    ).lower()



    if provider == "openrouter":

        api_key = os.getenv(
            "OPENROUTER_API_KEY"
        )

        api_url = os.getenv(
            "OPENROUTER_URL",
            DEFAULT_OPENROUTER_URL
        )

        model = os.getenv(
            "OPENROUTER_MODEL",
            "meta-llama/llama-3.3-70b-instruct"
        )



    else:

        api_key = os.getenv(
            "GROQ_API_KEY"
        )

        api_url = os.getenv(
            "GROQ_URL",
            DEFAULT_GROQ_URL
        )

        model = os.getenv(
            "GROQ_MODEL",
            "llama-3.3-70b-versatile"
        )



    if not api_key:

        raise Exception(
            f"{provider.upper()} API key missing"
        )



    payload = {

        "model": model,

        "messages": messages,

        "temperature": 0.3

    }



    headers = {

        "Authorization":
            f"Bearer {api_key}",

        "Content-Type":
            "application/json"

    }



    try:

        response = requests.post(

            api_url,

            json=payload,

            headers=headers,

            timeout=30

        )


        response.raise_for_status()



    except requests.RequestException as error:

        raise Exception(
            f"LLM request failed: {error}"
        )



    data = response.json()



    try:

        return (
            data["choices"][0]
            ["message"]
            ["content"]
        )


    except (KeyError, IndexError):

        raise Exception(
            "Invalid LLM response format"
        )