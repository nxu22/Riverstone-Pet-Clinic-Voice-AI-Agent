"""Phase 2 acceptance test — run with: venv/Scripts/python scripts/test_phase2.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
SLOT = "2026-06-29T09:00:00"  # Monday
NEW_SLOT = "2026-06-29T10:00:00"

print("\n--- Phase 2 API tests ---\n")

# [1] book a valid appointment
r = client.post("/book", json={
    "owner_name": "Sarah Chen",
    "pet_name": "Mochi",
    "species": "cat",
    "date_time": SLOT,
    "phone": "204-555-1234",
})
assert r.status_code == 201, f"Expected 201, got {r.status_code}: {r.text}"
code = r.json()["confirmation_code"]
print(f"[1] PASS  POST /book           => {code}  vet: {r.json()['vet_name']}")

# [2] look up by confirmation code
r = client.get(f"/lookup/{code}")
assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
print(f"[2] PASS  GET  /lookup/{code}  => {r.json()['owner_name']} / {r.json()['pet_name']}")

# [3] double-book same slot → 409
r = client.post("/book", json={
    "owner_name": "John Park",
    "pet_name": "Buddy",
    "species": "dog",
    "date_time": SLOT,
    "phone": "204-555-9999",
})
assert r.status_code == 409, f"Expected 409, got {r.status_code}: {r.text}"
print(f"[3] PASS  POST /book (conflict) => 409  '{r.json()['detail']}'")

# [4] look up a fake code → 404
r = client.get("/lookup/RST-0000")
assert r.status_code == 404, f"Expected 404, got {r.status_code}: {r.text}"
print(f"[4] PASS  GET  /lookup/RST-0000 => 404  '{r.json()['detail']}'")

# [5] reschedule to a new slot
r = client.patch("/reschedule", json={
    "confirmation_code": code,
    "new_date_time": NEW_SLOT,
})
assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
new_code = r.json()["confirmation_code"]
print(f"[5] PASS  PATCH /reschedule    => new code {new_code}  time: {r.json()['date_time']}")

# [6] cancel
r = client.delete(f"/cancel/{new_code}")
assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
print(f"[6] PASS  DELETE /cancel/{new_code}")

# [7] cancel again → 404
r = client.delete(f"/cancel/{new_code}")
assert r.status_code == 404, f"Expected 404, got {r.status_code}: {r.text}"
print(f"[7] PASS  DELETE /cancel again  => 404  '{r.json()['detail']}'")

# [8] invalid species → 422 (FastAPI auto-validates)
r = client.post("/book", json={
    "owner_name": "Test",
    "pet_name": "Test",
    "species": "dragon",
    "date_time": SLOT,
    "phone": "204-000-0000",
})
assert r.status_code == 422, f"Expected 422, got {r.status_code}: {r.text}"
print(f"[8] PASS  POST /book (bad species) => 422 auto-rejected")

print("\n>>> Phase 2 complete — all endpoints work!\n")
