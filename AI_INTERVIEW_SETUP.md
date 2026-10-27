# AI check-in configuration

The interview backend uses an OpenAI-compatible chat-completions API. The model only proposes a conversational reply and candidate facts; the server accepts a fact only when its category/field exists in `engine/schema.py`, its type/range is valid, and its evidence is an exact substring of the user's latest message. The burnout engine remains the only scoring component.

## Groq setup

Set these variables on the **backend host** (for local development, in `mindguard-backend/.env`, which must not be committed):

```text
LLM_PROVIDER=groq
GROQ_API_KEY=your-Groq-key
GROQ_MODEL=openai/gpt-oss-120b
