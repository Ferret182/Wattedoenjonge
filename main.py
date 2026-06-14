import os
from fastapi import FastAPI
from supabase import create_client

app = FastAPI()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
db = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/events")
def get_events():
    result = db.table("events").select("*").execute()
    return result.data