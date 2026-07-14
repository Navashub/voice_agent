from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from app.telephony.twilio_handler import router as twilio_router
from app.telephony.media_bridge import router as media_router

app = FastAPI(title="Voice Agent")
app.include_router(twilio_router)
app.include_router(media_router)


@app.get("/health")
def health():
    return {"status": "ok"}
