from .llm_connector import ask_llm, FALLBACK_QUESTIONS_MAP
from .prompt_builder import build_prompt
from .state_manager import create_state, update_state
from .extractor import extract_facts
from .completion_checker import is_complete


def _fallback_reply(state):
    missing = state.get("missing", [])
    if missing:
        return FALLBACK_QUESTIONS_MAP.get(
            missing[0],
            "Tell me more about how you've been feeling.",
        )
    return "Thank you for sharing. I think I have enough information now."


def process_message(message, state=None, tone="supportive"):

    if state is None:
        state = create_state()

    state.setdefault("history", [])
    state.setdefault("data", {})
    state.setdefault("missing", [])
    state.setdefault("completed", [])

    # Store student message
    state["history"].append(
        {
            "role": "student",
            "content": message
        }
    )

    # Extract facts from student turns only, before asking the next question,
    # so the prompt can steer towards what is still missing.
    combined_text = "\n".join(
        item["content"]
        for item in state["history"]
        if item.get("role") == "student"
    )

    facts = extract_facts(combined_text)
    state = update_state(state, facts)

    # -----------------------------
    # Completion check
    # -----------------------------
    if is_complete(state):
        return {
            "complete": True,
            "data": state["data"],
            "state": state
        }

    # -----------------------------
    # Ask LLM to conduct interview
    # -----------------------------
    prompt = build_prompt(
        state["history"],
        state,
        message,
        tone=tone,
    )

    try:
        reply = ask_llm(prompt, state)
    except Exception:
        # A missing/invalid API key or a provider outage should not break
        # the interview. Fall back to the next deterministic question.
        reply = _fallback_reply(state)

    if not reply:
        reply = _fallback_reply(state)

    # Store AI response
    state["history"].append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    return {
        "complete": False,
        "reply": reply,
        "state": state
    }
