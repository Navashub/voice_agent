"""
Every route is scoped by tenant_id in the URL, so one Twilio number per
client maps to /voice/incoming/{tenant_id} — same code, different tenant.

To add a new client later: buy a Twilio number, point its "A call comes in"
webhook at https://your-domain/voice/incoming/{new_tenant_id}, add the
tenant's config + knowledge base. Nothing here changes.
"""

import os

from fastapi import APIRouter, Request, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Connect

from app.tenants.config_loader import get_tenant_config

router = APIRouter()


@router.post("/voice/incoming/{tenant_id}")
async def incoming_call(tenant_id: str, request: Request):
    response = VoiceResponse()

    try:
        get_tenant_config(tenant_id)
    except ValueError:
        # Misconfigured Twilio number pointing at an unknown tenant_id —
        # fail gracefully for the caller, loudly in the logs.
        print(f"[ERROR] Incoming call for unknown tenant_id: {tenant_id}")
        response.say("Sorry, this line is not set up correctly. Please try again later.")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    host = request.headers.get("host")
    connect = Connect()
    connect.stream(url=f"wss://{host}/voice/media-stream/{tenant_id}")
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")


@router.post("/voice/status/{tenant_id}")
async def call_status(tenant_id: str, request: Request):
    form = await request.form()
    print(f"[{tenant_id}] call status update: {dict(form)}")
    return Response(status_code=204)


def place_outbound_call(tenant_id: str, to_number: str, from_number: str, base_url: str) -> str:
    """
    v1: connects straight to the agent, no answering-machine branching yet.
    Before this goes near real leads, add machine_detection + an
    amd-result webhook that hangs up / leaves a message on voicemail
    instead of talking to it — flagged as a follow-up, not done here.
    """
    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    call = client.calls.create(
        to=to_number,
        from_=from_number,
        url=f"{base_url}/voice/incoming/{tenant_id}",
        status_callback=f"{base_url}/voice/status/{tenant_id}",
    )
    return call.sid


@router.post("/voice/outbound/{tenant_id}")
async def trigger_outbound(tenant_id: str, request: Request):
    get_tenant_config(tenant_id)
    body = await request.json()
    to_number = body["to_number"]
    from_number = body["from_number"]
    base_url = f"https://{request.headers.get('host')}"

    call_sid = place_outbound_call(tenant_id, to_number, from_number, base_url)
    return {"call_sid": call_sid}
