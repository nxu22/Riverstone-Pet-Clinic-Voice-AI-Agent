import json
import os
from fastapi import APIRouter, HTTPException, Request
from retell import Retell

from app.calendar_provider import route_species_to_vet
from app.models import Appointment, Species
from app.sqlite_provider import SQLiteCalendarProvider

router = APIRouter()
calendar = SQLiteCalendarProvider()
retell_client = Retell(api_key=os.getenv("RETELL_API_KEY", ""))


def _result(text: str) -> dict:
    return {"result": text}


@router.post("/retell-webhook")
async def retell_webhook(request: Request):
    # 1. read raw body BEFORE any parsing
    raw_body = await request.body()
    signature = request.headers.get("x-retell-signature", "")

    # 2. verify signature — must use raw bytes, not re-serialised JSON
    if not retell_client.verify(
        body=raw_body.decode(),
        api_key=os.getenv("RETELL_API_KEY", ""),
        signature=signature,
    ):
        raise HTTPException(status_code=401, detail="Invalid signature.")

    # 3. parse JSON only after signature check passes
    data = json.loads(raw_body)
    name: str = data.get("name", "")
    args: dict = data.get("args", {})

    # 4. route to the right function
    if name == "book_appointment":
        return _handle_book(args)
    if name == "lookup_appointment":
        return _handle_lookup(args)
    if name == "reschedule_appointment":
        return _handle_reschedule(args)
    if name == "cancel_appointment":
        return _handle_cancel(args)

    return _result(f"Unknown function: {name}")


# ── handlers ──────────────────────────────────────────────────────────────────

def _handle_book(args: dict) -> dict:
    try:
        species = Species(args["species"])
        vet_name = route_species_to_vet(species)
        from datetime import datetime
        appt = calendar.create_appointment(Appointment(
            confirmation_code="",
            owner_name=args["owner_name"],
            pet_name=args["pet_name"],
            species=species,
            vet_name=vet_name,
            date_time=datetime.fromisoformat(args["date_time"]),
            phone=args["phone"],
        ))
        return _result(
            f"Appointment confirmed! Code: {appt.confirmation_code}. "
            f"{appt.vet_name} will see {appt.pet_name} on "
            f"{appt.date_time.strftime('%B %d at %I:%M %p')}."
        )
    except ValueError as e:
        return _result(f"Sorry, that time slot is not available. {e} Please choose another time.")


def _handle_lookup(args: dict) -> dict:
    code = args.get("confirmation_code", "").upper()
    appt = calendar.get_appointment(code)
    if not appt:
        return _result(f"Sorry, I couldn't find an appointment with code {code}.")
    return _result(
        f"Found it! {appt.owner_name}'s {appt.pet_name} is booked with "
        f"{appt.vet_name} on {appt.date_time.strftime('%B %d at %I:%M %p')}."
    )


def _handle_reschedule(args: dict) -> dict:
    from datetime import datetime
    code = args.get("confirmation_code", "").upper()
    existing = calendar.get_appointment(code)
    if not existing:
        return _result(f"Sorry, I couldn't find an appointment with code {code}.")

    calendar.cancel_appointment(code)
    try:
        new_appt = calendar.create_appointment(Appointment(
            confirmation_code="",
            owner_name=existing.owner_name,
            pet_name=existing.pet_name,
            species=existing.species,
            vet_name=existing.vet_name,
            date_time=datetime.fromisoformat(args["new_date_time"]),
            phone=existing.phone,
        ))
        return _result(
            f"Rescheduled! New code: {new_appt.confirmation_code}. "
            f"{new_appt.vet_name} will see {new_appt.pet_name} on "
            f"{new_appt.date_time.strftime('%B %d at %I:%M %p')}."
        )
    except ValueError as e:
        calendar.create_appointment(existing)
        return _result(f"Sorry, that new time is not available. {e} The original appointment is still in place.")


def _handle_cancel(args: dict) -> dict:
    code = args.get("confirmation_code", "").upper()
    found = calendar.cancel_appointment(code)
    if not found:
        return _result(f"Sorry, I couldn't find an appointment with code {code}.")
    return _result(f"Done! Appointment {code} has been cancelled.")
