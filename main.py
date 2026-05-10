from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import os
from dotenv import load_dotenv
from twilio.rest import Client as TwilioClient
from utils import get_or_create_user, log_transaction, update_balance, get_balance
from ai import parse_expense

load_dotenv()

app = FastAPI()

twilio_client = TwilioClient(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

def send_whatsapp_message(to_number: str, message: str):
    """Send WhatsApp message via Twilio"""
    twilio_client.messages.create(
        from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
        to=f"whatsapp:{to_number}",
        body=message
    )

@app.post("/webhook/twilio")
async def twilio_webhook(request: Request):
    """Receive WhatsApp messages from Twilio"""
    form_data = await request.form()

    user_phone = form_data.get("From", "").replace("whatsapp:", "")
    message_body = form_data.get("Body", "").strip()

    print(f"Message from {user_phone}: {message_body}")

    user = get_or_create_user(user_phone)
    user_id = user["id"]

    if user["is_paused"] and message_body.lower() not in ["bot chalu karo", "help"]:
        twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
        return PlainTextResponse(twiml, media_type="application/xml")

    balance = get_balance(user_id)

    if message_body.lower() == "hi":
        reply = "Paisa track karna chahte ho?\n\nPaise kaise aate hain tere paas?\n1️⃣ Parents monthly\n2️⃣ Jab maango\n3️⃣ Scholarship"
        send_whatsapp_message(user_phone, reply)

    elif message_body.lower() in ["kitna bacha hai", "balance", "bata"]:
        reply = f"₹{balance} bacha hai. 💰"
        send_whatsapp_message(user_phone, reply)

    else:
        parsed = parse_expense(message_body)

        if parsed.get("confidence", 0) > 0.7:
            amount = parsed.get("amount")
            type_ = parsed.get("type", "expense")
            bucket = parsed.get("bucket", "misc")
            description = parsed.get("description", "unknown")

            if type_ == "expense":
                log_transaction(user_id, amount, "expense", bucket, description)
                new_balance = update_balance(user_id, -amount)
                reply = f"₹{amount} {bucket} ✅\n₹{new_balance} bacha hai."
            else:
                log_transaction(user_id, amount, "income", None, description)
                new_balance = update_balance(user_id, amount)
                reply = f"₹{amount} aaye 🙌\n₹{new_balance} balance."

            send_whatsapp_message(user_phone, reply)
        else:
            send_whatsapp_message(user_phone, "Kitna tha? 🤔")

    twiml = '<?xml version="1.0" encoding="UTF-8"?><Response></Response>'
    return PlainTextResponse(twiml, media_type="application/xml")

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)