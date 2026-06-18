from datetime import datetime
from pydantic import BaseModel
from app.models import Species


class BookRequest(BaseModel):
    owner_name: str
    pet_name: str
    species: Species
    date_time: datetime
    phone: str


class BookResponse(BaseModel):
    confirmation_code: str
    owner_name: str
    pet_name: str
    vet_name: str
    date_time: datetime
    message: str


class AppointmentResponse(BaseModel):
    confirmation_code: str
    owner_name: str
    pet_name: str
    species: Species
    vet_name: str
    date_time: datetime
    phone: str


class RescheduleRequest(BaseModel):
    confirmation_code: str
    new_date_time: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: str
