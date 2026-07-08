"""
MindGuard AI Burnout Engine

Schema Definition

Single source of truth for Burnout Engine.

Defines:
- Categories
- Fields
- Types
- Orientation
- Required status
- Valid ranges

No calculations.
No normalization.
No scoring.
"""


ENGINE_SCHEMA = {


    "sleep": {

        "hours": {
            "type": "continuous",
            "min": 3,
            "max": 10,
            "required": True,
            "orientation": "positive"
        },

        "quality": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        },

        "rested": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        },

        "consistency": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "academic_load": {

        "study_hours": {
            "type": "continuous",
            "min": 0,
            "max": 16,
            "required": True,
            "orientation": "negative"
        },

        "homework_load": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        },

        "assignments": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        },

        "projects": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        },

        "upcoming_exams": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        },

        "subject_difficulty": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        },

        "academic_expectations": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        },

        "attendance": {
            "type": "percentage",
            "required": True,
            "orientation": "positive"
        }

    },


    "emotional_exhaustion": {

        "feeling_drained": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        },

        "recovery_after_rest": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "burnout_symptoms": {

        "overwhelmed": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        },

        "loss_of_interest": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        }

    },


    "motivation": {

        "study_motivation": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "cognitive": {

        "concentration": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        },

        "memory": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "stress": {

        "stress_frequency": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        },

        "stress_control": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "anxiety": {

        "worry_frequency": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        }

    },


    "mood": {

        "positive_mood": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "productivity": {

        "task_completion": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "time_management": {

        "planning": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "recent_life_events": {

        "major_changes": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        }

    },


    "personality_traits": {

        "perfectionism_pressure": {
            "type": "ordinal",
            "required": True,
            "orientation": "negative"
        }

    },


    "digital_behaviour": {

        "screen_time_control": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "lifestyle": {

        "daily_routine": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "social_support": {

        "support_availability": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    },


    "exercise": {

        "physical_activity": {
            "type": "ordinal",
            "required": True,
            "orientation": "positive"
        }

    }

}