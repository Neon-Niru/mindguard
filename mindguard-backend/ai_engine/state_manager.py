"""
MindGuard AI

Interview State Manager

Responsibility:

Track:
- collected information
- completed categories
- missing categories
- conversation history

Does NOT:
- calculate burnout
- score responses
- make decisions
"""


REQUIRED_INTERVIEW_CATEGORIES = [

    "academic_load",

    "sleep",

    "stress",

    "motivation",

    "mood",

    "cognitive",

    "lifestyle",

    "time_management",

    "social_support",

    "digital_behaviour",

    "recent_life_events",

    "emotional_exhaustion",

    "burnout_symptoms",

    "anxiety",

    "productivity",

    "exercise"

]



def create_state():

    return {

        "data": {},

        "completed": [],

        "missing": REQUIRED_INTERVIEW_CATEGORIES.copy(),

        "history": []

    }




def update_state(state, extracted):


    if not extracted:

        return state



    for category, values in extracted.items():


        if category not in state["data"]:

            state["data"][category] = {}



        if isinstance(values, dict):

            state["data"][category].update(values)


        else:

            state["data"][category] = values



        if category in state["missing"]:

            state["missing"].remove(category)

            state["completed"].append(category)



    return state




def is_complete(state):

    return len(state["missing"]) == 0




def get_missing_categories(state):

    return state["missing"]