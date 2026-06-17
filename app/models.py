from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class Species(str, Enum):
    cat = "cat"
    dog = "dog"
    rabbit = "rabbit"
    bird = "bird"
    reptile = "reptile"


class Vet(BaseModel):
    name: str
    specialty: str  # "small_animals" or "exotics"


class Appointment(BaseModel):
    id: int | None = None
    confirmation_code: str
    owner_name: str
    pet_name: str
    species: Species
    vet_name: str
    date_time: datetime
    phone: str
