"""
MindGuard AI

Recovery Mapping Layer

Responsibility:

Contributor categories
        ↓
Recovery focus areas

No scoring.
No AI.
No diagnosis.
"""


RECOVERY_MAPPING = {


    "sleep": [

        "Improve sleep consistency",

        "Maintain a regular bedtime",

        "Reduce late-night screen usage"

    ],


    "academic_load": [

        "Reduce workload overload",

        "Break assignments into smaller tasks",

        "Plan study sessions ahead"

    ],


    "emotional_exhaustion": [

        "Schedule mental recovery breaks",

        "Avoid prolonged study sessions",

        "Include daily relaxation"

    ],


    "burnout_symptoms": [

        "Restore study-life balance",

        "Reconnect with enjoyable activities",

        "Reduce continuous pressure"

    ],


    "motivation": [

        "Use small achievable goals",

        "Start with easiest task",

        "Track daily progress"

    ],


    "cognitive": [

        "Reduce distractions",

        "Use focused study intervals",

        "Take regular breaks"

    ],


    "stress": [

        "Practice stress management",

        "Prioritize important tasks",

        "Limit unnecessary pressure"

    ],


    "anxiety": [

        "Prepare earlier for exams",

        "Use calming techniques",

        "Avoid last-minute studying"

    ],


    "mood": [

        "Schedule enjoyable activities",

        "Maintain social interaction",

        "Balance academics and leisure"

    ],


    "productivity": [

        "Use a daily planner",

        "Prioritize important work",

        "Complete one task at a time"

    ],


    "time_management": [

        "Create a daily schedule",

        "Avoid procrastination",

        "Plan weekly goals"

    ],


    "recent_life_events": [

        "Reduce additional workload",

        "Allow recovery time",

        "Seek trusted support"

    ],


    "personality_traits": [

        "Reduce perfectionism",

        "Set realistic expectations",

        "Accept gradual improvement"

    ],


    "digital_behaviour": [

        "Limit recreational screen time",

        "Avoid late-night scrolling",

        "Use focus mode while studying"

    ],


    "lifestyle": [

        "Stay hydrated",

        "Exercise regularly",

        "Eat balanced meals"

    ],


    "social_support": [

        "Talk with trusted friends",

        "Reach out to family",

        "Connect with teachers"

    ],


    "exercise": [

        "Walk daily",

        "Light physical activity",

        "Stretch between study sessions"

    ]

}




def map_recovery_focus(contributors):

    """

    Receives ranked contributor data.

    Returns recovery focus areas.

    """


    ranked = sorted(

        contributors.items(),

        key=lambda item: item[1],

        reverse=True

    )


    primary_contributors = []

    recovery_focus = []


    for category, contribution in ranked:


        if contribution <= 0:

            continue


        primary_contributors.append(

            category.replace("_", " ").title()

        )


        if category in RECOVERY_MAPPING:

            recovery_focus.extend(

                RECOVERY_MAPPING[category]

            )


        if len(primary_contributors) >= 3:

            break



    return {

        "primary_contributors": primary_contributors,

        "recovery_focus_areas": recovery_focus[:3]

    }




# Backwards compatibility

def generate(contributions):

    return map_recovery_focus(contributions)