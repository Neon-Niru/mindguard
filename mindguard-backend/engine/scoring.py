from .config import (
    CATEGORY_WEIGHTS,
    PROTECTIVE_FACTOR_WEIGHTS,
    RISK_THRESHOLDS,
)
from .schema import ENGINE_SCHEMA


def _get_category_field_names():
    fields = {}
    for cat, schema_fields in ENGINE_SCHEMA.items():
        fields[cat] = list(schema_fields.keys())
    return fields


CATEGORY_FIELDS = _get_category_field_names()


def category_score(values):
    """Average the health values present in one category.

    Returns None when there is nothing usable, so partially collected
    interviews are scored only from what was actually reported.
    """
    numeric_values = [
        value for value in values
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    ]
    if not numeric_values:
        return None
    return round(sum(numeric_values) / len(numeric_values), 2)


def calculate_category_scores(normalized):
    scores = {}

    for category, category_data in normalized.items():
        if category not in ENGINE_SCHEMA or not isinstance(category_data, dict):
            continue

        score = category_score(list(category_data.values()))
        if score is not None:
            scores[category] = score

    return scores


def calculate_burnout(scores):
    burnout = 0.0
    contributions = {}

    available = {
        category: weight
        for category, weight in CATEGORY_WEIGHTS.items()
        if category in scores
    }
    total_weight = sum(available.values())

    if total_weight > 0:
        for category, weight in available.items():
            share = (100 - scores[category]) * (weight / total_weight)
            contributions[category] = round(share, 2)
            burnout += share

    protective_reduction = 0.0
    for category, weight in PROTECTIVE_FACTOR_WEIGHTS.items():
        if category in scores:
            protective_reduction += scores[category] * weight

    burnout = max(0.0, min(100.0, burnout - protective_reduction))
    wellness = 100.0 - burnout

    all_weights = sum(CATEGORY_WEIGHTS.values()) + sum(
        PROTECTIVE_FACTOR_WEIGHTS.values()
    )
    assessed_weight = sum(
        weight for category, weight in CATEGORY_WEIGHTS.items()
        if category in scores
    ) + sum(
        weight for category, weight in PROTECTIVE_FACTOR_WEIGHTS.items()
        if category in scores
    )

    return {
        "burnout_score": round(burnout),
        "wellness_score": round(wellness),
        "category_scores": scores,
        "contributions": contributions,
        "categories_assessed": len(scores),
        "data_completeness": round(assessed_weight / all_weights, 3)
        if all_weights else 0.0,
    }


def calculate_burnout_score(category_scores):
    result = calculate_burnout(category_scores)
    return result["burnout_score"]


def classify_risk(score):
    moderate_min = RISK_THRESHOLDS["MODERATE"]["min"]
    high_min = RISK_THRESHOLDS["HIGH"]["min"]

    if score >= high_min:
        return "High"
    if score >= moderate_min:
        return "Moderate"
    return "Low"


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
