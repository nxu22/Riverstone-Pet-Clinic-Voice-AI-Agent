# ROADMAP — Riverstone Pet Clinic Voice Agent

This is the **map**. Each phase has: a goal, what we build, why it matters, and
**"done when"** (how we know we can move on). We build **bottom-up**: the brain and the
backend first, the voice last.

`📍 You are here: Phase 0`

---

## Phase 0 — Foundation & orientation  ← START HERE
- **Goal:** a clean, runnable project skeleton.
- **Build:** virtual env, FastAPI app, folder structure, `.env` + `.gitignore`, a `/health` endpoint.
- **Why:** something that runs end-to-end (even if it does nothing yet) removes friction for everything after.
- **Done when:** `uvicorn` serves `/health` locally and returns OK.
- [x] venv created, FastAPI + uvicorn installed
- [x] folder structure agreed
- [x] `/health` endpoint runs locally

## Phase 1 — Domain model & calendar core
- **Goal:** the scheduling "brain" — no voice, no HTTP yet.
- **Build:** data models (Vet, Appointment, confirmation code), species→vet routing,
  `CalendarProvider` interface + SQLite implementation, 30-min slot generation, seed data.
- **Why:** this is the actual product. Everything else is plumbing around it.
- **Done when:** in a small test/REPL you can list open slots and create one appointment.
- [x] models defined
- [x] `CalendarProvider` interface + SQLite impl
- [x] slot generation (Mon–Fri 9–17, 30-min)
- [x] seed data + species→vet routing

## Phase 2 — Booking actions as an API
- **Goal:** book / look-up / reschedule / cancel over HTTP.
- **Build:** FastAPI endpoints for each action, confirmation-code generation, validation, conflict handling.
- **Why:** Retell will call these by webhook. Proving them with `curl` first is far faster than over a phone.
- **Done when:** you can run the full lifecycle (book → look up → reschedule → cancel) with `curl`/a test script.
- [x] book endpoint
- [x] look-up endpoint (by confirmation code)
- [x] reschedule endpoint
- [x] cancel endpoint

## Phase 3 — Retell custom-function webhook
- **Goal:** bridge the voice layer's "tool calls" to your FastAPI.
- **Build:** the webhook endpoint Retell calls, request/response shaped to Retell's format, signature check.
- **Why:** this bridge is the #1 source of voice-agent bugs — format mismatches. Get it right in isolation.
- **Done when:** a simulated Retell payload (posted via curl) triggers a real booking.
- [x] webhook endpoint
- [x] request/response mapping to Retell format
- [x] signature verification

## Phase 4 — Conversation design (Claude Haiku)
- **Goal:** the agent's brain & personality.
- **Build:** system prompt, FAQ knowledge, booking flow, species detection, emergency redirect,
  out-of-scope guardrails (no medical advice).
- **Why:** a voice agent is only as good as its prompt. This is where the demo shines or fails.
- **Done when:** a text-only conversation simulation books correctly and refuses out-of-scope asks.
- [x] system prompt + FAQ
- [x] booking flow logic
- [x] guardrails (emergency redirect, no medical advice)

## Phase 5 — Voice integration (Retell + ElevenLabs)
- **Goal:** make it actually talk.
- **Build:** Retell agent config, ElevenLabs voice, connect agent → webhook, phone number.
- **Why:** the demo's wow factor.
- **Done when:** you call a number and complete a booking by voice.
- [ ] Retell agent configured
- [ ] ElevenLabs voice chosen
- [ ] agent wired to your webhook + phone number

## Phase 6 — Post-booking automation (n8n + CRM)
- **Goal:** the "end-to-end" proof.
- **Build:** FastAPI fires HTTP to n8n on success; n8n sends confirmation email + writes to CRM.
- **Why:** shows no-code automation + CRM integration — a real selling point to clients.
- **Done when:** a booking produces a confirmation email AND a CRM contact.
- [ ] FastAPI → n8n trigger on success
- [ ] n8n: confirmation email
- [ ] n8n: CRM write (HubSpot / GoHighLevel)

## Phase 7 — Polish & demo
- **Goal:** portfolio-ready.
- **Build:** finalize README, demo script, record 2–3 min video, edge-case cleanup.
- **Why:** a portfolio project that isn't demoed doesn't exist.
- **Done when:** clean repo + a short demo video that states "mock-data demo" verbally.
- [ ] edge cases handled
- [ ] demo script
- [ ] demo video recorded
