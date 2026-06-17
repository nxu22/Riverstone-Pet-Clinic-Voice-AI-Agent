# CLAUDE.md — Riverstone Pet Clinic Voice Agent

> Claude Code reads this file automatically at the start of every session.
> It provides project context and conventions.

## What this project is
An AI **voice receptionist** for a fictional vet clinic (Riverstone Pet Clinic, Winnipeg).
A pet owner calls, the AI answers FAQs and **books / reschedules / cancels** appointments
by voice. On a successful booking, an automation sends a confirmation email and writes
the client into a CRM. This is a portfolio demo of an end-to-end voice agent.

## Stack
- **Voice orchestration:** Retell
- **Voice (TTS):** ElevenLabs
- **Conversation logic:** Claude 4.5 Haiku
- **Action backend:** FastAPI (Python)
- **Storage (dev):** SQLite, behind a swappable `CalendarProvider` interface
- **Automation:** n8n → confirmation email + CRM write (HubSpot / GoHighLevel)

## Architecture (data flow)
```
Owner ──call──▶ Retell (ASR + TTS via ElevenLabs) ──▶ Claude 4.5 Haiku
                                                          │ (decides to call a tool)
                                                          ▼
                                          Custom Function (webhook) ──▶ FastAPI backend
                                                                              │
                                                                  CalendarProvider (SQLite)
                                                                              │
                                                  on success ──HTTP──▶ n8n ──▶ email + CRM
```
**Build order is bottom-up:** backend + booking logic first (testable with curl), voice last.
The phone layer is the *last* thing we add — debugging logic over a live call is painful.

## Conventions
- Python 3.11+, FastAPI, `venv` + `pip`
- SQLite for dev (file `riverstone.db`), accessed only through `CalendarProvider`
- Timezone: **America/Winnipeg** everywhere
- Clinic rules:
  - Hours **Mon–Fri 09:00–17:00**, **30-minute** slots
  - `Dr. Okafor` → small animals (cats & dogs)
  - `Dr. Liang` → exotics (rabbits, birds, reptiles)
- **Mock data only.** No real PII, no payment processing, **no medical advice/diagnosis/triage**.
  Suspected emergency → tell caller to hang up and contact an animal ER.
- Secrets in `.env` (gitignored), never hardcoded.

## Working notes
- The phased plan lives in `ROADMAP.md`. Work in small, reviewable steps and check off
  items in `ROADMAP.md` as each phase completes.

## Current status
**Phase 1 — DONE.** Models, SQLite calendar provider, slot generation, conflict check all passing. Next: Phase 2 — booking API endpoints.
