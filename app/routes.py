import os
import httpx
from datetime import date
from fastapi import APIRouter, HTTPException
from app.calendar_provider import route_species_to_vet
from app.models import Appointment, Species
from app.schemas import (
    AppointmentResponse, BookRequest, BookResponse,
    RescheduleRequest,
)
from app.sqlite_provider import SQLiteCalendarProvider

router = APIRouter()
calendar = SQLiteCalendarProvider()


def _notify_n8n(appt: Appointment) -> None:
    url = os.getenv("N8N_WEBHOOK_URL", "").strip()
    if not url:
        return
    payload = {
        "confirmation_code": appt.confirmation_code,
        "owner_name": appt.owner_name,
        "pet_name": appt.pet_name,
        "species": appt.species.value,
        "vet": appt.vet_name,
        "appointment_time": appt.date_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "phone": appt.phone,
    }
    try:
        httpx.post(url, json=payload, timeout=5)
        print(f"n8n notified: {appt.confirmation_code}")
    except Exception as e:
        print(f"n8n notification failed (booking still OK): {e}")


@router.get("/availability")
def availability(species: str, date: date):
    try:
        vet_name = route_species_to_vet(Species(species))
    except ValueError:
        raise HTTPException(status_code=422, detail=f"Unknown species: {species}")
    slots = calendar.get_available_slots(date, vet_name)
    return {
        "vet": vet_name,
        "date": str(date),
        "available_slots": [s.strftime("%H:%M") for s in slots],
    }


@router.post("/book", response_model=BookResponse, status_code=201)
def book(req: BookRequest):
    vet_name = route_species_to_vet(req.species)
    try:
        appt = calendar.create_appointment(Appointment(
            confirmation_code="",
            owner_name=req.owner_name,
            pet_name=req.pet_name,
            species=req.species,
            vet_name=vet_name,
            date_time=req.date_time,
            phone=req.phone,
        ))
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    _notify_n8n(appt)
    return BookResponse(
        confirmation_code=appt.confirmation_code,
        owner_name=appt.owner_name,
        pet_name=appt.pet_name,
        vet_name=appt.vet_name,
        date_time=appt.date_time,
        message=f"Appointment confirmed for {appt.pet_name} with {appt.vet_name}.",
    )


@router.get("/lookup/{confirmation_code}", response_model=AppointmentResponse)
def lookup(confirmation_code: str):
    appt = calendar.get_appointment(confirmation_code.upper())
    if not appt:
        raise HTTPException(status_code=404, detail=f"No appointment found for code {confirmation_code}.")
    return AppointmentResponse(**appt.model_dump())


@router.patch("/reschedule", response_model=BookResponse)
def reschedule(req: RescheduleRequest):
    existing = calendar.get_appointment(req.confirmation_code.upper())
    if not existing:
        raise HTTPException(status_code=404, detail=f"No appointment found for code {req.confirmation_code}.")

    calendar.cancel_appointment(req.confirmation_code.upper())

    try:
        new_appt = calendar.create_appointment(Appointment(
            confirmation_code="",
            owner_name=existing.owner_name,
            pet_name=existing.pet_name,
            species=existing.species,
            vet_name=existing.vet_name,
            date_time=req.new_date_time,
            phone=existing.phone,
        ))
    except ValueError as e:
        # new slot is taken — restore original booking
        calendar.create_appointment(existing)
        raise HTTPException(status_code=409, detail=str(e))

    return BookResponse(
        confirmation_code=new_appt.confirmation_code,
        owner_name=new_appt.owner_name,
        pet_name=new_appt.pet_name,
        vet_name=new_appt.vet_name,
        date_time=new_appt.date_time,
        message=f"Rescheduled for {new_appt.pet_name} with {new_appt.vet_name}.",
    )


@router.delete("/cancel/{confirmation_code}")
def cancel(confirmation_code: str):
    found = calendar.cancel_appointment(confirmation_code.upper())
    if not found:
        raise HTTPException(status_code=404, detail=f"No appointment found for code {confirmation_code}.")
    return {"message": f"Appointment {confirmation_code.upper()} has been cancelled."}


@router.get("/appointments")
def list_appointments():
    with calendar._connect() as conn:
        rows = conn.execute(
            "SELECT * FROM appointments ORDER BY created_at DESC, id DESC"
        ).fetchall()
    result = []
    for row in rows:
        r = dict(row)
        if r.get("created_at"):
            r["created_at"] = r["created_at"].replace(" ", "T")
        if r.get("date_time"):
            r["date_time"] = r["date_time"].replace(" ", "T")
        result.append(r)
    return result
