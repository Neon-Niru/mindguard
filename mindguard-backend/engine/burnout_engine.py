"""
MindGuard AI

Main Burnout Engine

Pipeline

Validation
↓
Normalization
↓
Category Scoring
↓
Burnout Score
↓
Risk
↓
Contributors
↓
Recovery
↓
Summaries
↓
JSON Report

The engine is deterministic and never calls an LLM.
Missing categories are allowed; only reported categories are scored and
the contributing weights are renormalised over what is available.
"""


from .config import ENGINE_VERSION

from .validators import validate_payload

from .normalizer import normalize_payload

from .scoring import (
    calculate_category_scores,
    calculate_burnout,
    classify_risk,
    rank_contributors,
)

from .recovery_mapper import map_recovery_focus

from .summaries import generate_category_summaries


class BurnoutEngine:

    @staticmethod
    def generate_report(raw_payload: dict):

        # ----------------------------
        # Validation
        # ----------------------------

        validate_payload(raw_payload, require_all=False)

        # ----------------------------
        # Normalization
        # ----------------------------

        normalized = normalize_payload(raw_payload)

        # ----------------------------
        # Category Scoring
        # ----------------------------

        category_scores = calculate_category_scores(normalized)

        # ----------------------------
        # Burnout Calculation
        # ----------------------------

        burnout_result = calculate_burnout(category_scores)

        burnout_score = burnout_result["burnout_score"]
        wellness_score = burnout_result["wellness_score"]

        # ----------------------------
        # Risk Classification
        # ----------------------------

        risk_level = classify_risk(burnout_score)

        # ----------------------------
        # Contribution Analysis
        # ----------------------------

        contributors = rank_contributors(category_scores)

        # ----------------------------
        # Recovery Mapping
        # ----------------------------

        recovery_focus = map_recovery_focus(contributors)

        # ----------------------------
        # Summaries
        # ----------------------------

        summaries = generate_category_summaries(category_scores)

        # ----------------------------
        # Final Report
        # ----------------------------

        return {

            "burnout_score": burnout_score,

            "wellness_score": wellness_score,

            "risk_level": risk_level,

            "engine_version": ENGINE_VERSION,

            "category_scores": category_scores,

            "contributions": burnout_result["contributions"],

            "categories_assessed": burnout_result["categories_assessed"],

            "data_completeness": burnout_result["data_completeness"],

            "sleep_score":
                category_scores.get("sleep"),

            "stress_score":
                category_scores.get("stress"),

            "motivation_score":
                category_scores.get("motivation"),

            "academic_load_score":
                category_scores.get("academic_load"),

            "emotional_exhaustion_score":
                category_scores.get("emotional_exhaustion"),

            "cognitive_score":
                category_scores.get("cognitive"),

            "lifestyle_score":
                category_scores.get("lifestyle"),

            "mental_energy_score":
                category_scores.get("burnout_symptoms"),

            "mood_score":
                category_scores.get("mood"),

            "productivity_score":
                category_scores.get("productivity"),

            "primary_contributors":
                recovery_focus.get("primary_contributors", []),

            "recovery_focus_areas":
                recovery_focus.get("recovery_focus_areas", []),

            "category_summaries":
                summaries

        }
