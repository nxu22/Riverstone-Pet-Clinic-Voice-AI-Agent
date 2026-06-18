"""
Phase 4 conversation simulation.
Run with: venv/Scripts/python scripts/test_phase4.py
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import os
from dotenv import load_dotenv
load_dotenv()

import anthropic
from app.prompt import SYSTEM_PROMPT

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
SYSTEM = SYSTEM_PROMPT.replace("{{current_date}}", "Monday, June 29, 2026")


def turn(history: list[dict], user_says: str) -> str:
    """Send one user turn and return River's reply."""
    history.append({"role": "user", "content": user_says})
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system=SYSTEM,
        messages=history,
    )
    reply = resp.content[0].text
    history.append({"role": "assistant", "content": reply})
    return reply


def scenario(title: str, turns: list[str]):
    print(f"\n{'='*60}")
    print(f"SCENARIO: {title}")
    print("="*60)
    history = []
    for user_msg in turns:
        print(f"\nCaller : {user_msg}")
        reply = turn(history, user_msg)
        print(f"River  : {reply}")


# [1] simple FAQ
scenario("FAQ - clinic hours", [
    "Hi, what are your hours?",
])

# [2] FAQ - exotics
scenario("FAQ - do you see rabbits?", [
    "Do you see exotic animals like rabbits?",
])

# [3] Emergency redirect - must transfer, NOT offer booking
scenario("EMERGENCY - dog collapsed", [
    "My dog collapsed and isn't breathing. What should I do?",
])

# [4] Emergency redirect - subtle case
scenario("EMERGENCY - cat in pain", [
    "My cat seems to be in a lot of pain and can't stand up.",
])

# [5] Booking flow - collect species and date
scenario("BOOKING - start flow", [
    "I'd like to make an appointment.",
    "It's for my cat.",
    "How about this Wednesday?",
])

# [6] Out of scope - medical question during booking
scenario("GUARDRAIL - medical question", [
    "My dog has been sneezing a lot. Is that serious?",
])

print("\n>>> Phase 4 simulation complete.\n")
