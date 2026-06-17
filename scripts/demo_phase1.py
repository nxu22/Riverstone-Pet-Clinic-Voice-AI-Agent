"""Phase 1 acceptance test — run with: venv/Scripts/python scripts/demo_phase1.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from datetime import date
from app.models import Appointment, Species
from app.sqlite_provider import SQLiteCalendarProvider
from app.calendar_provider import route_species_to_vet

db = SQLiteCalendarProvider("riverstone.db")
day = date(2026, 6, 23)  # Monday

# ── Step 1: list available slots ──────────────────────────────────────────────
vet = route_species_to_vet(Species.cat)  # Dr. Okafor
slots = db.get_available_slots(day, vet)
print(f"\n[1] Available slots for {vet} on {day} ({len(slots)} total)")
for s in slots[:4]:
    print(f"   {s.strftime('%H:%M')}")
print("   ...")

# ── Step 2: book the 09:00 slot ───────────────────────────────────────────────
booked = db.create_appointment(Appointment(
    confirmation_code="",
    owner_name="Sarah Chen",
    pet_name="Mochi",
    species=Species.cat,
    vet_name=vet,
    date_time=slots[0],
    phone="204-555-1234",
))
print(f"\n[2] Booked!  Code: {booked.confirmation_code}  "
      f"Time: {booked.date_time.strftime('%H:%M')}  Vet: {booked.vet_name}")

# ── Step 3: look up by confirmation code ──────────────────────────────────────
found = db.get_appointment(booked.confirmation_code)
print(f"\n[3] Look-up {booked.confirmation_code}: "
      f"{found.owner_name} / {found.pet_name} at {found.date_time.strftime('%H:%M')}")

# ── Step 4: try to double-book the same slot (should be rejected) ─────────────
print(f"\n[4] Trying to double-book {slots[0].strftime('%H:%M')} ...")
try:
    db.create_appointment(Appointment(
        confirmation_code="",
        owner_name="John Park",
        pet_name="Buddy",
        species=Species.dog,
        vet_name=vet,
        date_time=slots[0],
        phone="204-555-9999",
    ))
    print("   FAIL: double-booking was allowed — this should not happen!")
except ValueError as e:
    print(f"   PASS: correctly rejected: {e}")

# ── Step 5: cancel and confirm slot returns ───────────────────────────────────
db.cancel_appointment(booked.confirmation_code)
slots_after = db.get_available_slots(day, vet)
restored = slots[0] in slots_after
print(f"\n[5] Cancelled {booked.confirmation_code}")
print(f"   Slot restored: {'PASS' if restored else 'FAIL'}")
print(f"   Slots available now: {len(slots_after)}")

print("\n>>> Phase 1 complete — calendar core works!\n")
