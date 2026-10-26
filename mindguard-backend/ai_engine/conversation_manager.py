from .llm_connector import ask_llm
from .prompt_builder import build_prompt
from .state_manager import create_state, update_state
from .extractor import extract_facts, extract_contextual
from .completion_checker import is_complete
from .fallback import explain, looks_confused, next_question, topic_for_question


def _fallback_reply(state, prefer=None):
    question = next_question(state, prefer=prefer)
    if question:
        return question
    return "Thank you for sharing. I think I have enough information now."


def process_message(message, state=None, tone="supportive"):

    if state is None:
        state = create_state()

    state.setdefault("history", [])
    state.setdefault("data", {})
    state.setdefault("missing", [])
    state.setdefault("completed", [])
    state.setdefault("asked", {})
    state.setdefault("last_question", "")
    state.setdefault("last_topic", None)

    # The question the student is answering right now, before history grows.
    previous_topic = state.get("last_topic")

    # Store student message
    state["history"].append(
        {
            "role": "student",
            "content": message
        }
    )

    # A short answer ("ok", "heavy", "5 hours") only means something relative
    # to the question that was just asked. A confused reply ("huh?", "why?")
    # is not an answer, so it must not be bound to that topic — unless the
    # message also contains an actual answer ("what? it's heavy").
    explicit_now = extract_facts(message)
    contextual = (
        extract_contextual(message, previous_topic)
        if previous_topic else {}
    )
    asking_again = looks_confused(message)
    confused = asking_again and not explicit_now and not contextual

    # Extract facts from student turns only, before asking the next question,
    # so the prompt can steer towards what is still missing.
    combined_text = "\n".join(
        item["content"]
        for item in state["history"]
        if item.get("role") == "student"
    )

    facts = extract_facts(
        combined_text,
        topic=previous_topic,
        latest=message,
    )
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
    # The student is not answering
    # -----------------------------
    # Explain why the question matters, then re-ask the same topic in the
    # other phrasing (or move on once it has been probed enough).
    if confused:
        reply = f"{explain(previous_topic)} {_fallback_reply(state, prefer=previous_topic)}"

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
        reply = None

    if reply:
        # The LLM chooses its own wording, so the remembered topic has to come
        # from the text itself; otherwise the next terse answer would bind to
        # the question the fallback asked earlier.
        topic = topic_for_question(reply)
        state["last_question"] = reply
        state["last_topic"] = topic
        if topic:
            asked = state.setdefault("asked", {})
            asked[topic] = asked.get(topic, 0) + 1
    else:
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
