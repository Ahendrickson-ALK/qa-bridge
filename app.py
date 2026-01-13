from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()

@app.post("/answer")
async def answer():
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>This is a QA training call. Your bridge is working.</Say>
</Response>
"""
    return Response(content=twiml, media_type="application/xml")
