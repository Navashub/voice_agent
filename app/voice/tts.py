from openai import OpenAI

from app.voice.audio_utils import wav_bytes_to_mulaw_8k

client = OpenAI()


def synthesize_to_mulaw(text: str, voice: str = "coral") -> bytes:
    """Synthesizes speech and returns 8kHz mulaw bytes ready to stream to Twilio."""
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        instructions="Speak warmly and clearly, like a helpful receptionist. Moderate pace.",
        response_format="wav",
    )
    wav_bytes = response.read() if hasattr(response, "read") else response.content
    return wav_bytes_to_mulaw_8k(wav_bytes)
