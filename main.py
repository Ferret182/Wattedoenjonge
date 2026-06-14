# main.py
from fastapi import FastAPI
from supabase import create_client

app = FastAPI()

SUPABASE_URL = "https://lxkvotweebvcsmzzlvgk.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx4a3ZvdHdlZWJ2Y3NtenpsdmdrIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE0Mjg1MjUsImV4cCI6MjA5NzAwNDUyNX0.-vyNrS08AiMSYcxWi8_-isKUuj-rTTSvdXfwptUeZEs"
db = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/events")
def get_events():
    result = db.table("events").select("*").execute()
    return result.data