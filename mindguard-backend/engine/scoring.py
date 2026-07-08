from .config import CATEGORY_WEIGHTS


CATEGORY_FIELDS = {

    "sleep": [
        "hours",
        "quality",
        "rested",
        "consistency"
    ],

    "academic_load": [
        "study_hours",
        "homework_load",
        "assignments",
        "projects",
        "upcoming_exams",
        "subject_difficulty",
        "academic_expectations",
        "attendance"
    ],

    "emotional_exhaustion": [],

    "burnout_symptoms": [],

    "motivation": [],

    "cognitive": [],

    "stress": [],

    "anxiety": [],

    "mood": [],

    "productivity": [],

    "time_management": [],

    "recent_life_events": [],

    "personality_traits": [],

    "digital_behaviour": [],

    "lifestyle": [],

    "social_support": [],

    "exercise": []

}



def category_score(values):

    if not values:
        return 0

    numeric_values = [
        value for value in values
        if isinstance(value, (int, float))
    ]

    if not numeric_values:
        return 0

    return round(
        sum(numeric_values) / len(numeric_values),
        2
    )



def calculate_category_scores(normalized):

    scores = {}


    for category in CATEGORY_FIELDS:

        category_data = normalized.get(
            category,
            {}
        )


        values = list(
            category_data.values()
        )


        scores[category] = category_score(values)


    return scores



def calculate_burnout(scores):

    burnout = 0

    contributions = {}


    for category, weight in CATEGORY_WEIGHTS.items():

        score = scores.get(
            category,
            0
        )


        # Normal categories:
        # Higher health score = lower burnout

        contribution = (
            (100 - score)
            *
            weight
        )


        contributions[category] = round(
            contribution,
            2
        )


        burnout += contribution



    burnout = max(
        0,
        min(
            100,
            burnout
        )
    )


    wellness = 100 - burnout


    return {

        "burnout_score": round(burnout),

        "wellness_score": round(wellness),

        "category_scores": scores,

        "contributions": contributions

    }



# Compatibility function used by burnout_engine.py

def calculate_burnout_score(category_scores):

    result = calculate_burnout(
        category_scores
    )

    return result["burnout_score"]



def classify_risk(score):

    if score < 30:
        return "Low"

    elif score < 60:
        return "Moderate"

    else:
        return "High"



def rank_contributors(category_scores):

    contributors = {}


    for category, score in category_scores.items():

        contributors[category] = round(
            100 - score,
            2
        )


    return dict(
        sorted(
            contributors.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )