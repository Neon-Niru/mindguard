from .llm_connector import ask_llm
from .prompt_builder import build_prompt
from .state_manager import create_state, update_state
from .extractor import extract_facts
from .completion_checker import is_complete



def process_message(message, state=None):


    if state is None:

        state = create_state()



    # Store student message

    state["history"].append(

        {
            "role": "student",
            "content": message
        }

    )



    # -----------------------------
    # Ask LLM to conduct interview
    # -----------------------------

    prompt = build_prompt(

        state["history"],

        state,

        message

    )


    reply = ask_llm(prompt)



    # Store AI response

    state["history"].append(

        {
            "role": "assistant",
            "content": reply
        }

    )



    # -----------------------------
    # Extract facts from conversation
    # -----------------------------

    combined_text = "\n".join(

        item["content"]

        for item in state["history"]

    )



    facts = extract_facts(

        combined_text

    )



    state = update_state(

        state,

        facts

    )



    # -----------------------------
    # Completion check
    # -----------------------------

    if is_complete(state):


        return {


            "complete": True,


            "data": state["data"],


            "state": state


        }



    return {


        "complete": False,


        "reply": reply,


        "state": state


    }