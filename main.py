from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
db = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.get("/events")
def get_events():
    result = db.table("events").select("*").execute()
    events = result.data

    non_recurring_dates = [
        date.fromisoformat(e["date"])
        for e in events
        if not e.get("recurring") and e.get("date")
    ]

    if non_recurring_dates:
        cutoff = max(non_recurring_dates)
    else:
        cutoff = date.today() + timedelta(weeks=4)

    expanded = []

    for event in events:
        if event.get("recurring") == "weekly":
            event_date = date.fromisoformat(event["date"])
            while event_date <= cutoff:
                new_event = event.copy()
                new_event["date"] = str(event_date)
                expanded.append(new_event)
                event_date += timedelta(weeks=1)
        else:
            expanded.append(event)

    return expanded


class EventSubmission(BaseModel):
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    date: Optional[str] = None
    starting_time: Optional[str] = None
    ending_time: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    contact: Optional[str] = None


@app.post("/submit")
def submit_event(event: EventSubmission):
    db.table("pending_events").insert(event.dict()).execute()
    return {"message": "Bedankt! Je evenement wordt beoordeeld."}


@app.get("/pending")
def get_pending():
    result = db.table("pending_events").select("*").order("submitted_at", desc=False).execute()
    return result.data


@app.post("/approve/{id}")
def approve_event(id: int):
    # Fetch the pending event
    result = db.table("pending_events").select("*").eq("id", id).execute()
    if not result.data:
        return {"error": "Not found"}, 404

    pending = result.data[0]

    # Remove fields that don't belong in events table
    pending.pop("id", None)
    pending.pop("submitted_at", None)
    pending.pop("contact", None)

    # Insert into events table
    db.table("events").insert(pending).execute()

    # Delete from pending
    db.table("pending_events").delete().eq("id", id).execute()

    return {"message": "Goedgekeurd"}


@app.delete("/reject/{id}")
def reject_event(id: int):
    db.table("pending_events").delete().eq("id", id).execute()
    return {"message": "Afgewezen"}
