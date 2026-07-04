from app.agent.tools.log_lead import run as log_lead


def run(state: dict) -> dict:
    log_lead(state)
    return {
        "status": "callback_booked",
        "message": (
            "I've noted your details. A member of our admissions team will "
            "call you back within the hour."
        ),
    }
