from abc import ABC, abstractmethod
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.models import Appointment, Species, Vet

TIMEZONE = ZoneInfo("America/Winnipeg")

CLINIC_OPEN = time(9, 0)
CLINIC_CLOSE = time(17, 0)
SLOT_MINUTES = 30

VETS = [
    Vet(name="Dr. Okafor", specialty="small_animals"),
    Vet(name="Dr. Liang", specialty="exotics"),
]

SPECIES_TO_VET = {
    Species.cat: "Dr. Okafor",
    Species.dog: "Dr. Okafor",
    Species.rabbit: "Dr. Liang",
    Species.bird: "Dr. Liang",
    Species.reptile: "Dr. Liang",
}


def route_species_to_vet(species: Species) -> str:
    return SPECIES_TO_VET[species]


def generate_slots(day: date) -> list[datetime]:
    """Return all 30-min slots for a clinic day. Empty list if weekend."""
    if day.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return []

    slots = []
    current = datetime.combine(day, CLINIC_OPEN, tzinfo=TIMEZONE)
    end = datetime.combine(day, CLINIC_CLOSE, tzinfo=TIMEZONE)

    while current < end:
        slots.append(current)
        current += timedelta(minutes=SLOT_MINUTES)

    return slots


class CalendarProvider(ABC):
    @abstractmethod
    def get_available_slots(self, day: date, vet_name: str) -> list[datetime]:
        """Return slots not yet booked for this vet on this day."""

    @abstractmethod
    def create_appointment(self, appointment: Appointment) -> Appointment:
        """Save appointment and return it with its assigned id."""

    @abstractmethod
    def get_appointment(self, confirmation_code: str) -> Appointment | None:
        """Look up by confirmation code."""

    @abstractmethod
    def cancel_appointment(self, confirmation_code: str) -> bool:
        """Cancel by confirmation code. Return True if found and cancelled."""
