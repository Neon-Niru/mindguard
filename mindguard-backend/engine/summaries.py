"""
MindGuard AI

Deterministic category summaries.

These summaries are generated ONLY from numeric scores.

Input:
Category health score
100 = healthiest
0 = poorest

No AI.
No diagnosis.
No interpretation.
"""

SUMMARY_RULES = {
    (0, 20): "High concern indicators are present.",
    (21, 40): "Elevated concerns are present.",
    (41, 60): "Moderate concerns are present.",
    (61, 80): "Minor concerns are present.",
    (81, 100): "Indicators are within a healthy range."
}


def generate_summary(health_score: float) -> str:
    """
    Accepts a HEALTH score (0–100).

    Higher score = healthier.
    """

    health_score = round(max(0, min(100, health_score)))

    for (low, high), text in SUMMARY_RULES.items():

        if low <= health_score <= high:
            return text

    return "No summary available."


def generate_category_summaries(category_scores: dict):

    summaries = {}

    for category, score in category_scores.items():

        summaries[f"{category}_summary"] = generate_summary(score)

    return summaries