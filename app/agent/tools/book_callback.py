from app.agent.tools.log_lead import run as log_lead


def run(state: dict) -> dict:
    log_lead(state)

    preferred_time = (state.get("lead_info") or {}).get("preferred_callback_time")
    if preferred_time:
        message = (
            f"I've noted your details. A member of our admissions team will "
            f"call you back {preferred_time}."
        )
    else:
        message = (
            "I've noted your details. A member of our admissions team will "
            "call you back within the hour."
        )

    return {"status": "callback_booked", "message": message}
