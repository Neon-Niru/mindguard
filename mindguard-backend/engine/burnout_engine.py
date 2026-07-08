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
"""


from .validators import validate_payload

from .normalizer import normalize_payload

from .scoring import (
    calculate_category_scores,
    calculate_burnout_score,
    classify_risk,
    rank_contributors,
)

from .recovery_mapper import map_recovery_focus

from .summaries import generate_category_summaries



ENGINE_VERSION = "1.0.0"



class BurnoutEngine:


    @staticmethod
    def generate_report(raw_payload: dict):


        # ----------------------------
        # Validation
        # ----------------------------

        validate_payload(raw_payload)



        # ----------------------------
        # Normalization
        # ----------------------------

        normalized = normalize_payload(
            raw_payload
        )



        # ----------------------------
        # Category Scoring
        # ----------------------------

        category_scores = calculate_category_scores(
            normalized
        )



        # ----------------------------
        # Burnout Calculation
        # ----------------------------

        burnout_score = calculate_burnout_score(
            category_scores
        )


        wellness_score = round(
            100 - burnout_score,
            2
        )



        # ----------------------------
        # Risk Classification
        # ----------------------------

        risk_level = classify_risk(
            burnout_score
        )



        # ----------------------------
        # Contribution Analysis
        # ----------------------------

        contributors = rank_contributors(
            category_scores
        )



        # ----------------------------
        # Recovery Mapping
        # ----------------------------

        recovery_focus = map_recovery_focus(
            contributors
        )



        # ----------------------------
        # Summaries
        # ----------------------------

        summaries = generate_category_summaries(
            category_scores
        )



        # ----------------------------
        # Final Report
        # ----------------------------

        return {

            "burnout_score": burnout_score,

            "wellness_score": wellness_score,

            "risk_level": risk_level,

            "engine_version": ENGINE_VERSION,


            "sleep_score":
                category_scores.get(
                    "sleep",
                    0
                ),


            "stress_score":
                category_scores.get(
                    "stress",
                    0
                ),


            "motivation_score":
                category_scores.get(
                    "motivation",
                    0
                ),


            "academic_load_score":
                category_scores.get(
                    "academic_load",
                    0
                ),


            "emotional_exhaustion_score":
                category_scores.get(
                    "emotional_exhaustion",
                    0
                ),


            "cognitive_score":
                category_scores.get(
                    "cognitive",
                    0
                ),


            "lifestyle_score":
                category_scores.get(
                    "lifestyle",
                    0
                ),


            "mental_energy_score":
                category_scores.get(
                    "burnout_symptoms",
                    0
                ),


            "mood_score":
                category_scores.get(
                    "mood",
                    0
                ),


            "productivity_score":
                category_scores.get(
                    "productivity",
                    0
                ),


            "primary_contributors":
                contributors,


            "recovery_focus_areas":
                recovery_focus,


            "category_summaries":
                summaries

        }