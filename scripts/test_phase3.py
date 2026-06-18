"""Phase 3 acceptance test — run with: venv/Scripts/python scripts/test_phase3.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

HEADERS = {"x-retell-signature": "test-sig", "Content-Type": "application/json"}

def post_webhook(payload: dict, verify_return: bool = True):
    with patch("app.retell_webhook.retell_client.verify", return_value=verify_return):
        return client.post("/retell-webhook", content=json.dumps(payload), headers=HEADERS)

print("\n--- Phase 3 Retell Webhook tests ---\n")

# [1] invalid signature -> 401
r = post_webhook({"name": "book_appointment", "args": {}, "call": {"call_id": "x"}}, verify_return=False)
assert r.status_code == 401, f"Expected 401, got {r.status_code}"
print(f"[1] PASS  Bad signature           => 401")

# [2] book via webhook
payload = {
    "name": "book_appointment",
    "args": {
        "owner_name": "Sarah Chen",
        "pet_name": "Mochi",
        "species": "cat",
        "date_time": "2026-07-07T09:00:00",
        "phone": "204-555-1234",
    },
    "call": {"call_id": "call_001"},
}
r = post_webhook(payload)
assert r.status_code == 200
result = r.json()["result"]
assert "RST-" in result, f"No confirmation code in result: {result}"
code = [w for w in result.split() if w.startswith("RST-")][0].rstrip(".")
print(f"[2] PASS  book_appointment        => {code}")

# [3] confirm booking truly reached Phase 2 (lookup by confirmation code)
r = client.get(f"/lookup/{code}")
assert r.status_code == 200, f"Lookup failed: {r.text}"
assert r.json()["owner_name"] == "Sarah Chen"
print(f"[3] PASS  webhook penetrates Phase 2 => lookup confirmed {r.json()['owner_name']} / {r.json()['pet_name']}")

# [4] lookup via webhook
r = post_webhook({"name": "lookup_appointment", "args": {"confirmation_code": code}, "call": {"call_id": "call_002"}})
assert r.status_code == 200
assert "Mochi" in r.json()["result"]
print(f"[4] PASS  lookup_appointment      => '{r.json()['result'][:60]}...'")

# [5] reschedule via webhook
r = post_webhook({
    "name": "reschedule_appointment",
    "args": {"confirmation_code": code, "new_date_time": "2026-07-07T10:00:00"},
    "call": {"call_id": "call_003"},
})
assert r.status_code == 200
result = r.json()["result"]
new_code = [w for w in result.split() if w.startswith("RST-")][0].rstrip(".")
print(f"[5] PASS  reschedule_appointment  => new code {new_code}")

# [6] cancel via webhook
r = post_webhook({"name": "cancel_appointment", "args": {"confirmation_code": new_code}, "call": {"call_id": "call_004"}})
assert r.status_code == 200
assert "cancelled" in r.json()["result"].lower()
print(f"[6] PASS  cancel_appointment      => '{r.json()['result']}'")

# [7] lookup after cancel -> not found message (result, not 404)
r = post_webhook({"name": "lookup_appointment", "args": {"confirmation_code": new_code}, "call": {"call_id": "call_005"}})
assert r.status_code == 200
assert "couldn't find" in r.json()["result"].lower()
print(f"[7] PASS  lookup after cancel     => '{r.json()['result']}'")

# [8] unknown function name -> graceful response
r = post_webhook({"name": "fly_to_moon", "args": {}, "call": {"call_id": "call_006"}})
assert r.status_code == 200
assert "Unknown" in r.json()["result"]
print(f"[8] PASS  unknown function        => '{r.json()['result']}'")

print("\n>>> Phase 3 complete — Retell webhook bridge works!\n")
