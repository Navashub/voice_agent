"""
Twilio Media Streams sends/expects 8kHz mono mulaw audio.
OpenAI's STT/TTS work with standard WAV (PCM16). These helpers convert
between the two so the rest of the code never has to think about codecs.
"""

import audioop
import io
import wave

TWILIO_SAMPLE_RATE = 8000


def mulaw_to_pcm16(mulaw_bytes: bytes) -> bytes:
    return audioop.ulaw2lin(mulaw_bytes, 2)


def pcm16_to_wav_bytes(pcm_bytes: bytes, sample_rate: int = TWILIO_SAMPLE_RATE) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


def wav_bytes_to_mulaw_8k(wav_bytes: bytes) -> bytes:
    """Convert an arbitrary WAV (any sample rate/width/channels) to 8kHz mono mulaw."""
    with wave.open(io.BytesIO(wav_bytes), "rb") as wf:
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frame_rate = wf.getframerate()
        pcm = wf.readframes(wf.getnframes())

    if channels == 2:
        pcm = audioop.tomono(pcm, sample_width, 0.5, 0.5)

    if sample_width != 2:
        pcm = audioop.lin2lin(pcm, sample_width, 2)
        sample_width = 2

    if frame_rate != TWILIO_SAMPLE_RATE:
        pcm, _ = audioop.ratecv(pcm, sample_width, 1, frame_rate, TWILIO_SAMPLE_RATE, None)

    return audioop.lin2ulaw(pcm, sample_width)


def rms(mulaw_bytes: bytes) -> int:
    """Rough loudness of a mulaw chunk — used for simple silence detection (VAD)."""
    pcm = mulaw_to_pcm16(mulaw_bytes)
    return audioop.rms(pcm, 2)
