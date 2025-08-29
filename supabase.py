import os
from supabase import create_client
from datetime import datetime

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

def save_user(user_info, ip):
    data = {
        "id": user_info["id"],
        "username": f'{user_info["username"]}#{user_info["discriminator"]}',
        "email": user_info.get("email"),
        "ip": ip,
        "timestamp": datetime.utcnow().isoformat()
    }
    supabase.table("users").upsert(data).execute()

def get_user(user_id):
    res = supabase.table("users").select("*").eq("id", user_id).execute()
    if res.data:
        return res.data[0]
    return None
