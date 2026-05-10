import hashlib
from supabase import create_client, Client
import os

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def hash_phone(phone: str) -> str:
    """Hash phone number for privacy"""
    return hashlib.sha256(phone.encode()).hexdigest()

def get_or_create_user(phone: str):
    """Get user from DB or create if new"""
    phone_hash = hash_phone(phone)
    response = supabase.table("users").select("*").eq("phone_hash", phone_hash).execute()
    if response.data:
        return response.data[0]
    else:
        new_user = supabase.table("users").insert({
            "phone_hash": phone_hash,
            "money_type": "monthly",
            "monthly_budget": 0,
            "current_balance": 0,
        }).execute()
        return new_user.data[0]

def log_transaction(user_id: str, amount: int, type: str, bucket: str,
                    description: str, merchant: str = None):
    """Log a transaction"""
    supabase.table("transactions").insert({
        "user_id": user_id,
        "amount": amount,
        "type": type,
        "bucket": bucket,
        "description": description,
        "merchant": merchant,
        "logged_by": "user_manual"
    }).execute()

def get_balance(user_id: str):
    """Get current balance"""
    user = supabase.table("users").select("current_balance").eq("id", user_id).execute()
    return user.data[0]["current_balance"] if user.data else 0

def update_balance(user_id: str, change: int):
    """Update balance — positive for income, negative for expense"""
    current = get_balance(user_id)
    new_balance = current + change
    supabase.table("users").update({"current_balance": new_balance}).eq("id", user_id).execute()
    return new_balance