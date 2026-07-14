import io

from openai import OpenAI

from app.voice.audio_utils import pcm16_to_wav_bytes

client = OpenAI()


def transcribe_pcm16(pcm_bytes: bytes, sample_rate: int = 8000) -> str:
    """Transcribes one buffered utterance. Called once per caller turn
    (after silence is detected), not continuously — see media_bridge.py."""
    wav_bytes = pcm16_to_wav_bytes(pcm_bytes, sample_rate)
    audio_file = io.BytesIO(wav_bytes)
    audio_file.name = "utterance.wav"

    result = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file,
    )
    return result.text.strip()
