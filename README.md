# Riverstone Pet Clinic — Voice AI Receptionist

A production-style voice AI agent that answers calls for a (fictional) pet clinic: it checks real appointment availability, books, looks up, reschedules, and cancels appointments — entirely by voice — writes everything to a real backend with a live dashboard, and **automatically sends a confirmation email and logs each client to a CRM**.

> Built to demonstrate end-to-end voice-agent engineering: conversation design, tool/function calling, signature-verified webhooks, anti-hallucination guardrails, a backend that is the single source of truth, and a decoupled post-booking automation layer.

## Demo

[![Watch the demo](https://cdn-cf-east.streamable.com/image/wrv0mb.jpg)](https://streamable.com/wrv0mb)

## What it does

- **Natural voice conversation** — the agent ("River") speaks in a warm, professional tone and drives a step-by-step booking flow.
- **Real availability** — slots come from the backend/database, never guessed by the model.
- **Full appointment lifecycle** — book, look up, reschedule, and cancel, each by a unique confirmation code (`RST-NNNN`).
- **Species → vet routing** — Dr. Okafor (cats & dogs), Dr. Liang (rabbits, birds, reptiles).
- **Same-day awareness** — when asked about "today," the backend filters out time slots that have already passed.
- **Safety guardrails** — refuses medical advice, redirects emergencies to an animal ER, declines phone payments, and never invents clinic policies.
- **Live dashboard** — a web page that polls the API and shows new bookings appear in real time.
- **Post-booking automation** — every confirmed booking automatically triggers a **confirmation email (Resend)** and writes the client to a **CRM (Airtable)** via an **n8n** workflow.

## Architecture

```
Caller (web call; phone-ready via Retell)
      │  voice
      ▼
 ┌──────────┐   text ↔ speech   ┌──────────────┐
 │  Retell  │ ◀──────────────▶  │  ElevenLabs  │  (voice / TTS)
 │  (ASR)   │                   └──────────────┘
 └────┬─────┘
      │ transcript
      ▼
 Claude 4.5 Haiku        (conversation + decides which tool to call)
      │ function call (JSON)
      ▼
 POST /retell-webhook    ← verified with X-Retell-Signature (raw body)
      │
      ▼
 FastAPI backend ───────► SQLite  (appointments, source of truth)
      │
      ├──► Live dashboard   (/dashboard polls /appointments)
      │
      └──► n8n workflow (self-hosted)   ← fail-safe POST on each booking
                 ├──► Resend    (confirmation email to client)
                 └──► Airtable  (CRM record)
```

**Tech stack:** Retell (voice orchestration) · Claude 4.5 Haiku (conversation) · ElevenLabs (voice) · FastAPI + Python · SQLite · n8n (self-hosted, post-booking automation) · Resend (email) · Airtable (CRM) · ngrok (dev tunnel)

## Engineering challenges (and how I solved them)

**1. Webhook signature verification (401 "Invalid signature").** Retell signs every function call with `X-Retell-Signature`. Verification kept failing — and the real cause wasn't the key itself but that `load_dotenv()` ran *after* the module imported, so the API key was empty at verification time. Fixed by loading the environment early and verifying against the **raw request body** (re-serializing the JSON changes the bytes and breaks the signature). The 401 rejection is enforced, so only genuinely signed requests are processed.

**2. Date reasoning (the agent kept booking the wrong day).** LLMs are unreliable at turning "this Monday" into an actual calendar date — the model confidently computed dates that were off by a day. Solution: **take date math away from the model entirely.** The agent passes the caller's exact words (e.g. "this monday"), and the backend resolves them to a real date using Python + the `America/Winnipeg` timezone. The agent never states a date it computed itself; it only speaks the date the tool returns. The backend is the source of truth.

**3. Same-day slot filtering.** When the resolved date is today, the backend drops slots whose time has already passed (with a buffer), so the agent never offers a 9 AM appointment at 3 PM.

**4. Anti-hallucination guardrails.** The agent may only state facts that are in its prompt or come back from a tool — it can't invent clinic policies (e.g. "we don't do same-day appointments") or make up availability. Availability is decided only by the `check_availability` result.

**5. Decoupled post-booking automation.** Side effects (email, CRM, and anything added later) live in an **n8n** workflow rather than the request handler. On a successful booking the backend fires a **fail-safe** POST to n8n — failures are logged and can never block or break a booking — and n8n fans out to Resend and Airtable. New steps (SMS, Slack, analytics) can be added by editing the workflow, without touching application code.

## Project structure

```
app/
  main.py              # FastAPI app + routes mounting + live dashboard
  routes.py            # HTTP API (book / lookup / reschedule / cancel / appointments)
  retell_webhook.py    # Retell function webhook + signature verification + n8n notify
  calendar_provider.py # slot generation + booking logic (interface)
  sqlite_provider.py   # SQLite-backed calendar provider
  models.py            # domain models (Species, Vet, Appointment)
  schemas.py           # request/response schemas
  prompt.py            # the agent's system prompt (River)
riverstone.db          # SQLite database (dev, gitignored)
requirements.txt
.env                   # RETELL_API_KEY, N8N_WEBHOOK_URL, etc. (not committed)
```

## Running it locally

```bash
# 1. setup
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. configure — create a .env file with:
#   RETELL_API_KEY=your_retell_webhook_key
#   N8N_WEBHOOK_URL=your_n8n_production_webhook_url   (optional; blank disables automation)

# 3. run the backend
uvicorn app.main:app --host 127.0.0.1 --port 8000

# 4. expose it for Retell to reach
ngrok http 8000
# → use the public URL + /retell-webhook as the function URL in Retell
```

**Retell agent setup:** Single-Prompt agent · model Claude 4.5 Haiku · an ElevenLabs voice · paste `app/prompt.py` into the System Prompt · add 5 custom functions (`check_availability`, `book_appointment`, `lookup_appointment`, `reschedule_appointment`, `cancel_appointment`), all pointing at the webhook URL · inject the current time with the `{{current_time_America/Winnipeg}}` dynamic variable.

**n8n automation setup:** self-hosted n8n (Docker) · a Webhook trigger node fans out to a Resend "Send a new email" node (confirmation email) and an Airtable "Create a record" node (CRM). Point `N8N_WEBHOOK_URL` in `.env` at the workflow's **production** URL and publish the workflow.

The live dashboard is at `http://127.0.0.1:8000/dashboard`.

## Notes

Riverstone Pet Clinic is fictional and uses mock data. The agent does not give medical advice, does not handle real payments, and redirects emergencies to a real animal emergency hospital. Clinic hours are Monday–Friday, 9 AM–5 PM.

---

[Portfolio](https://nanxu.site) · [GitHub](https://github.com/nxu22) · [LinkedIn](https://linkedin.com/in/n-xu)
