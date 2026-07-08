"""
MindGuard AI
Global Burnout Engine Configuration

Contains:
- Engine version
- Category weights
- Protective factor weights
- Risk thresholds

No calculations.
No scoring logic.
"""


ENGINE_VERSION = "1.0.0"



# Burnout contributing categories
# Higher weight = greater influence

CATEGORY_WEIGHTS = {

    "emotional_exhaustion": 0.25,

    "academic_load": 0.15,

    "sleep": 0.15,

    "burnout_symptoms": 0.15,

    "motivation": 0.08,

    "cognitive": 0.06,

    "stress": 0.05,

    "anxiety": 0.03,

    "mood": 0.03,

    "productivity": 0.03,

    "time_management": 0.03,

    "recent_life_events": 0.02,

    "personality_traits": 0.02,

    "digital_behaviour": 0.02,

    "lifestyle": 0.02

}



# Protective factors
# These reduce burnout score.
# They are NOT burnout contributors.

PROTECTIVE_FACTOR_WEIGHTS = {

    "social_support": 0.02,

    "exercise": 0.01

}



# Configurable risk classification

RISK_THRESHOLDS = {

    "LOW": {

        "min": 0,

        "max": 34

    },


    "MODERATE": {

        "min": 35,

        "max": 64

    },


    "HIGH": {

        "min": 65,

        "max": 100

    }

}