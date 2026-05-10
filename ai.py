import os
from groq import Groq
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_expense(message: str, context: dict = None):
    """Parse Hinglish expense message with Groq"""

    system_prompt = """Tu ek Hinglish expense parser hai.

User ke message se extract karo:
- amount (sirf number)
- type ('expense' ya 'income')
- bucket (essentials/social/personal/debts/misc)
- description (1-2 words — jo user ne kaha)
- confidence (0.0 to 1.0)

Bucket rules:
- essentials: khana, food, transport, recharge, medicines, rent
- social: movies, trips, cafe, party, entertainment
- personal: cigg, cigarette, haircut, gym, clothes
- debts: diya kisi ko, lend, borrow, sent home
- misc: unclear, unknown

Income indicators: "mila", "aaya", "bheje", "received", "scholarship"

Agar amount unclear → confidence below 0.5

Return SIRF JSON. Koi explanation nahi.

Examples:
Input: "180 ka swiggy kiya"
Output: {"amount":180,"type":"expense","bucket":"essentials","description":"swiggy","confidence":0.95}

Input: "mummy ne 8000 bheje"
Output: {"amount":8000,"type":"income","bucket":null,"description":"from mummy","confidence":0.98}"""

    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[{"role": "user", "content": message}],
        temperature=0.1,
        max_tokens=200
    )

    try:
        text = response.choices[0].message.content.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"Parse error: {e}")
        return {"amount": None, "type": "unknown", "confidence": 0}