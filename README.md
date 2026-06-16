# Riverstone Pet Clinic — Voice AI Agent

An AI **voice receptionist** for a (fictional) veterinary clinic. A pet owner calls in,
the AI answers, handles common questions, and **books / reschedules / cancels**
appointments by voice. After a successful booking, the system automatically emails
a confirmation and writes the client into a CRM.

**Stack:** Retell (voice orchestration) · ElevenLabs (voice) · Claude 4.5 Haiku
(conversational logic) · FastAPI (action backend) · n8n (post-booking automation) ·
HubSpot / GoHighLevel (CRM)

> **Why this exists:** a portfolio demo proving an end-to-end voice agent —
> voice + appointment booking + CRM integration + no-code automation — in one project.
> A pet clinic (rather than a medical clinic) keeps the privacy stakes low while
> demonstrating the exact same skills.

## 1. Project Overview

### 1.1 Business Setup (fictional)

- **Clinic:** Riverstone Pet Clinic (Winnipeg)
- **Two veterinarians / two scheduling pools:**
  - `Dr. Okafor` — Small Animals (cats & dogs)
  - `Dr. Liang` — Exotics (rabbits, birds, reptiles)
- **Hours:** Monday–Friday, 9:00–17:00, 30-minute slots
- **Timezone:** America/Winnipeg

### 1.2 What the AI Front Desk Can Do

| Capability | Description |
|---|---|
| **Answer FAQs** | Hours, location & parking, whether exotics are seen, vaccinations, after-hours referral to a 24h animal ER, payment methods, new-client info |
| **Book** | Detect the pet's species → route to the right vet → offer open slots → collect details → create the booking → read back a confirmation code |
| **Look up an appointment** | By owner last name + pet name, or by phone number |
| **Reschedule** | Move to a new slot using the confirmation code |
| **Cancel** | Cancel using the confirmation code |
| **Post-booking automation** | (n8n) Auto-send a confirmation email + write the client/pet into the CRM |

### 1.3 Out of Scope (important boundaries)

- **No medical advice, diagnosis, or triage.** For a suspected emergency, the agent
  tells the caller to hang up and contact an animal emergency hospital.
- This is a **mock-data demo**, not a compliant production system.
- **No payment processing** and no credit card handling.
