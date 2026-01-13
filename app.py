import os
import requests
from fastapi import FastAPI
from fastapi.responses import Response, FileResponse

app = FastAPI()

# Load environment variables from Render
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")
VOICE_ID = os.getenv("VOICE_ID")

# Temporary audio file path (Render allows writing to /tmp)
AUDIO_FILE = "/tmp/qa_audio.mp3"


def generate_audio(text: str = None):
    """
    Generate ElevenLabs audio and save it to AUDIO_FILE.
    If text is not provided, use default QA training text.
    """
    if text is None:
        text = "This is a QA training call. Please follow the normal service request process."

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Accept": "audio/mpeg",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_turbo_v2"
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Raise error if API fails

    # Save audio to file
    with open(AUDIO_FILE, "wb") as f:
        f.write(response.content)


@app.post("/answer")
def answer_call():
    """
    Twilio calls this endpoint. Generate audio and return TwiML to play it.
    """
    # Generate audio (always refresh)
    generate_audio()

    # TwiML to play the generated audio
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Play>https://{os.getenv('RENDER_EXTERNAL_URL')}/audio</Play>
</Response>
"""
    return Response(content=twiml, media_type="application/xml")


@app.get("/audio")
def serve_audio():
    """
    Serve the generated audio file.
    Generate it if it does not exist yet (optional safety).
    """
    if not os.path.exists(AUDIO_FILE):
        generate_audio()
    return FileResponse(
        AUDIO_FILE,
        media_type="audio/mpeg",
        filename="qa_audio.mp3"
    )
