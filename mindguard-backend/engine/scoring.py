from .config import CATEGORY_WEIGHTS
from .schema import ENGINE_SCHEMA


def _get_category_field_names():
    fields = {}
    for cat, schema_fields in ENGINE_SCHEMA.items():
        fields[cat] = list(schema_fields.keys())
    return fields


CATEGORY_FIELDS = _get_category_field_names()


def category_score(values):
    if not values:
        return 50
    numeric_values = [
        value for value in values
        if isinstance(value, (int, float))
    ]
    if not numeric_values:
        return 50
    return round(
        sum(numeric_values) / len(numeric_values),
        2
    )


def calculate_category_scores(normalized):
    scores = {}

    for category in CATEGORY_FIELDS:
        category_data = normalized.get(category, {})
        values = list(category_data.values())
        scores[category] = category_score(values)

    return scores


def calculate_burnout(scores):
    burnout = 0
    contributions = {}

    for category, weight in CATEGORY_WEIGHTS.items():
        score = scores.get(category, 50)
        contribution = (100 - score) * weight
        contributions[category] = round(contribution, 2)
        burnout += contribution

    for category, weight in {
        "social_support": 0.02,
        "exercise": 0.01
    }.items():
        score = scores.get(category, 50)
        boost = score * weight
        burnout -= boost

    burnout = max(0, min(100, burnout))
    wellness = 100 - burnout

    return {
        "burnout_score": round(burnout),
        "wellness_score": round(wellness),
        "category_scores": scores,
        "contributions": contributions
    }


def calculate_burnout_score(category_scores):
    result = calculate_burnout(category_scores)
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
        contributors[category] = round(100 - score, 2)

    return dict(
        sorted(
            contributors.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )
