from fastapi import APIRouter, HTTPException
from app.calendar_provider import route_species_to_vet
from app.models import Appointment
from app.schemas import (
    AppointmentResponse, BookRequest, BookResponse,
    RescheduleRequest,
)
from app.sqlite_provider import SQLiteCalendarProvider

router = APIRouter()
calendar = SQLiteCalendarProvider()


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
