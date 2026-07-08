"""
MindGuard AI Burnout Engine

Normalization Layer

Responsibility:
Convert validated factual inputs into standardized values.

This module:
- DOES NOT calculate burnout
- DOES NOT classify risk
- DOES NOT invent missing values
- DOES NOT use AI

Pipeline position:

Validation
    ↓
Normalization
    ↓
Category Scoring
"""


def normalize_payload(payload: dict):

    """
    Normalize validated payload.

    Current implementation preserves already
    structured factual values while providing
    the correct interface for the scoring layer.

    Category-specific normalization rules
    can be added here without modifying
    scoring or orchestration.
    """


    normalized = {}


    for category, fields in payload.items():

        normalized[category] = {}


        for field, value in fields.items():

            normalized[category][field] = value


    return normalized