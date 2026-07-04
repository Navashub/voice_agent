# FastAPI entrypoint - webhook routes live here
from fastapi import FastAPI

app = FastAPI(title="Voice Agent")

@app.get("/health")
def health():
    return {"status": "ok"}
