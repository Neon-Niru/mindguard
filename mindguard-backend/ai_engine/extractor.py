import json



def extract_facts(text: str):

    """
    Information Extraction Layer

    Responsibility:
    Convert conversation text into factual structured data.

    Rules:
    - No scoring
    - No burnout calculation
    - No diagnosis
    - No assumptions

    Output:
    Facts only.
    """



    facts = {}

    text_lower = text.lower()



    # -------------------------
    # Sleep
    # -------------------------

    if "sleep" in text_lower:

        sleep = {}


        if (
            "5 hour" in text_lower
            or
            "five hour" in text_lower
        ):

            sleep["hours"] = 5


        elif (
            "6 hour" in text_lower
            or
            "six hour" in text_lower
        ):

            sleep["hours"] = 6


        elif (
            "7 hour" in text_lower
            or
            "seven hour" in text_lower
        ):

            sleep["hours"] = 7


        if "poor" in text_lower:

            sleep["quality"] = "Poor"


        if "tired" in text_lower:

            sleep["rested"] = "Never"


        if "irregular" in text_lower:

            sleep["consistency"] = "Never"


        if sleep:

            facts["sleep"] = sleep





    # -------------------------
    # Motivation
    # -------------------------

    if (
        "no motivation" in text_lower
        or
        "don't feel like studying" in text_lower
        or
        "dont feel like studying" in text_lower
    ):


        facts["motivation"] = {

            "study_motivation": "low"

        }





    # -------------------------
    # Stress
    # -------------------------

    if "stress" in text_lower:


        facts["stress"] = {

            "stress_frequency": "reported"

        }





    # -------------------------
    # Mood
    # -------------------------

    if (
        "sad" in text_lower
        or
        "low mood" in text_lower
    ):


        facts["mood"] = {

            "mood_state": "low"

        }





    # -------------------------
    # Concentration
    # -------------------------

    if (
        "cannot focus" in text_lower
        or
        "can't focus" in text_lower
    ):


        facts["concentration"] = {

            "focus_level": "low"

        }





    # -------------------------
    # Lifestyle
    # -------------------------

    if (
        "exercise" in text_lower
        or
        "walk" in text_lower
    ):


        facts["lifestyle"] = {

            "physical_activity": "reported"

        }





    return facts





def clean_json(output):

    """
    Safely parse JSON output.
    """

    try:

        return json.loads(output)


    except (
        json.JSONDecodeError,
        TypeError
    ):

        return {}