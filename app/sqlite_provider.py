import random
import sqlite3
import string
from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.calendar_provider import CalendarProvider, TIMEZONE, generate_slots
from app.models import Appointment, Species


def _make_confirmation_code() -> str:
    digits = "".join(random.choices(string.digits, k=4))
    return f"RST-{digits}"


def _row_to_appointment(row: sqlite3.Row) -> Appointment:
    return Appointment(
        id=row["id"],
        confirmation_code=row["confirmation_code"],
        owner_name=row["owner_name"],
        pet_name=row["pet_name"],
        species=Species(row["species"]),
        vet_name=row["vet_name"],
        # parse ISO string and restore Winnipeg timezone
        date_time=datetime.fromisoformat(row["date_time"]).replace(tzinfo=TIMEZONE),
        phone=row["phone"],
    )


class SQLiteCalendarProvider(CalendarProvider):
    def __init__(self, db_path: str = "riverstone.db"):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    confirmation_code TEXT    NOT NULL UNIQUE,
                    owner_name       TEXT    NOT NULL,
                    pet_name         TEXT    NOT NULL,
                    species          TEXT    NOT NULL,
                    vet_name         TEXT    NOT NULL,
                    date_time        TEXT    NOT NULL,
                    phone            TEXT    NOT NULL
                )
            """)

    def get_available_slots(self, day: date, vet_name: str) -> list[datetime]:
        all_slots = generate_slots(day)
        if not all_slots:
            return []

        # fetch booked datetimes for this vet on this day
        day_str = day.isoformat()
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT date_time FROM appointments WHERE vet_name = ? AND date_time LIKE ?",
                (vet_name, f"{day_str}%"),
            ).fetchall()

        # booked set uses naive isoformat strings for fast lookup
        booked = {row["date_time"] for row in rows}

        # exclude slots whose isoformat (without tzinfo) is in booked
        return [
            slot for slot in all_slots
            if slot.replace(tzinfo=None).isoformat() not in booked
        ]

    def create_appointment(self, appointment: Appointment) -> Appointment:
        # check the slot is still available before writing
        available = self.get_available_slots(
            appointment.date_time.date(), appointment.vet_name
        )
        requested = appointment.date_time.replace(tzinfo=None)
        if not any(s.replace(tzinfo=None) == requested for s in available):
            raise ValueError(
                f"{appointment.vet_name} has no opening at "
                f"{appointment.date_time.strftime('%Y-%m-%d %H:%M')}. "
                "Please choose another slot."
            )

        code = _make_confirmation_code()
        # store datetime as naive ISO string — timezone is always Winnipeg
        dt_str = appointment.date_time.replace(tzinfo=None).isoformat()

        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO appointments
                  (confirmation_code, owner_name, pet_name, species, vet_name, date_time, phone)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    code,
                    appointment.owner_name,
                    appointment.pet_name,
                    appointment.species.value,
                    appointment.vet_name,
                    dt_str,
                    appointment.phone,
                ),
            )
            return appointment.model_copy(
                update={"id": cursor.lastrowid, "confirmation_code": code}
            )

    def get_appointment(self, confirmation_code: str) -> Appointment | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM appointments WHERE confirmation_code = ?",
                (confirmation_code,),
            ).fetchone()
        return _row_to_appointment(row) if row else None

    def cancel_appointment(self, confirmation_code: str) -> bool:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM appointments WHERE confirmation_code = ?",
                (confirmation_code,),
            )
        return cursor.rowcount > 0
