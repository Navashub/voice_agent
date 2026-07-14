"""
Bridges a Twilio Media Stream WebSocket to the LangGraph agent.

v1 approach: turn-based, not fully continuous streaming. Audio is buffered
while the caller is speaking; once ~500ms of silence is detected, the
buffered utterance is transcribed, run through the graph, and the reply is
synthesized and streamed back. This is simpler and more reliable to get
working first — true low-latency streaming transcription and barge-in
handling (interrupting playback when the caller starts talking) are real
improvements to make once this baseline works on a live call, not before.

State persistence follows the same pattern as chat_cli.py: lead_info and
messages persist for the whole call (keyed by tenant_id here, per-session
in memory), everything else resets each turn.
"""

import asyncio
import audioop
import base64
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.agent.graph import build_graph
from app.tenants.config_loader import get_tenant_config
from app.voice.audio_utils import rms
from app.voice.stt import transcribe_pcm16
from app.voice.tts import synthesize_to_mulaw

router = APIRouter()

_graph = build_graph()

# Tuning knobs — these will need adjusting against real call audio.
SILENCE_RMS_THRESHOLD = 300
SILENCE_CHUNKS_TO_END_TURN = 25   # ~25 * 20ms = 500ms of silence ends a turn
MIN_SPEECH_CHUNKS = 5             # ignore tiny noise blips
TWILIO_CHUNK_BYTES = 160          # 20ms of 8kHz mulaw audio


def fresh_state(tenant_id: str) -> dict:
    return {
        "tenant_id": tenant_id,
        "messages": [],
        "user_input": "",
        "intent": None,
        "retrieved_context": None,
        "tool_result": None,
        "response": None,
        "lead_info": {},
        "escalate": False,
    }


@router.websocket("/voice/media-stream/{tenant_id}")
async def media_stream(websocket: WebSocket, tenant_id: str):
    await websocket.accept()
    get_tenant_config(tenant_id)  # fail fast if tenant is unknown

    state = fresh_state(tenant_id)
    stream_sid = None

    audio_buffer = bytearray()
    silence_chunks = 0
    speech_chunks = 0
    speaking = False

    async def send_audio(mulaw_bytes: bytes):
        for i in range(0, len(mulaw_bytes), TWILIO_CHUNK_BYTES):
            chunk = mulaw_bytes[i:i + TWILIO_CHUNK_BYTES]
            payload = base64.b64encode(chunk).decode("utf-8")
            await websocket.send_text(json.dumps({
                "event": "media",
                "streamSid": stream_sid,
                "media": {"payload": payload},
            }))
            await asyncio.sleep(0.02)  # pace playback to real-time

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            event = msg.get("event")

            if event == "start":
                stream_sid = msg["start"]["streamSid"]

            elif event == "media":
                mulaw_chunk = base64.b64decode(msg["media"]["payload"])
                level = rms(mulaw_chunk)

                if level > SILENCE_RMS_THRESHOLD:
                    audio_buffer.extend(mulaw_chunk)
                    speech_chunks += 1
                    silence_chunks = 0
                    speaking = True
                elif speaking:
                    audio_buffer.extend(mulaw_chunk)
                    silence_chunks += 1

                    turn_complete = (
                        silence_chunks >= SILENCE_CHUNKS_TO_END_TURN
                        and speech_chunks >= MIN_SPEECH_CHUNKS
                    )
                    if turn_complete:
                        pcm = audioop.ulaw2lin(bytes(audio_buffer), 2)

                        audio_buffer = bytearray()
                        speech_chunks = 0
                        silence_chunks = 0
                        speaking = False

                        user_text = transcribe_pcm16(pcm)
                        if not user_text:
                            continue

                        # Reset per-turn fields, keep lead_info/messages persistent
                        state["user_input"] = user_text
                        state["intent"] = None
                        state["retrieved_context"] = None
                        state["tool_result"] = None
                        state["response"] = None
                        state["escalate"] = False
                        state["messages"].append({"role": "user", "content": user_text})

                        state = _graph.invoke(state)

                        state["messages"].append(
                            {"role": "assistant", "content": state["response"]}
                        )

                        reply_audio = synthesize_to_mulaw(state["response"])
                        await send_audio(reply_audio)

            elif event == "stop":
                break

    except WebSocketDisconnect:
        pass
