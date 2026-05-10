from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.post("/webhook/twilio")
async def twilio_webhook(request: Request):
    """Receive WhatsApp messages from Twilio"""
    form_data = await request.form()
    
    user_phone = form_data.get("From", "")
    message_body = form_data.get("Body", "")
    
    print(f"Message from {user_phone}: {message_body}")
    
    # For now, just echo back
    reply = f"Got your message: {message_body}"
    
    twiml = f'<?xml version="1.0" encoding="UTF-8"?><Response><Message>{reply}</Message></Response>'
    return PlainTextResponse(twiml, media_type="application/xml")

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)