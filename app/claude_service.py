"""Claude API integration.

Sends the ticket to Claude with the knowledge base and asks for JSON only.
If anything fails (bad key, network, malformed JSON), we return a safe
fallback so the ticket is still saved — the AI is an enhancement, not a
single point of failure.
"""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

from app.knowledge_base import KNOWLEDGE_BASE

load_dotenv()

MODEL = "claude-sonnet-4-6"

VALID_CATEGORIES = {"hardware", "software", "network", "access", "security", "other"}
VALID_PRIORITIES = {"P1", "P2", "P3", "P4"}

SYSTEM_PROMPT = f"""You are the triage engine for an IT helpdesk.

Use this knowledge base for categories, priority rules, and known fixes:

{KNOWLEDGE_BASE}

Given a ticket, respond with ONLY a JSON object — no markdown fences,
no preamble — in exactly this shape:

{{
  "category": "hardware|software|network|access|security|other",
  "priority": "P1|P2|P3|P4",
  "suggested_response": "A friendly, professional first reply to the requester. Greet them by name, acknowledge the issue, and give the most relevant next steps from the knowledge base. 2-5 sentences.",
  "reasoning": "One sentence explaining the category and priority choice."
}}
"""

FALLBACK = {
    "category": "unclassified",
    "priority": "P3",
    "suggested_response": None,
    "reasoning": "AI triage unavailable — classified manually pending review.",
}


def triage_ticket(requester_name: str, subject: str, description: str) -> dict:
    """Returns dict with keys: category, priority, suggested_response, reasoning."""
    try:
        client = Anthropic()  # reads ANTHROPIC_API_KEY from environment
        message = client.messages.create(
            model=MODEL,
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Requester name: {requester_name}\n"
                        f"Subject: {subject}\n"
                        f"Description: {description}"
                    ),
                }
            ],
        )

        raw = "".join(
            block.text for block in message.content if block.type == "text"
        )
        # Defensive: strip markdown fences if the model added them anyway
        raw = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(raw)

        # Validate before trusting — never let bad AI output corrupt your data
        if result.get("category") not in VALID_CATEGORIES:
            result["category"] = "other"
        if result.get("priority") not in VALID_PRIORITIES:
            result["priority"] = "P3"
        result.setdefault("suggested_response", None)
        result.setdefault("reasoning", None)
        return result

    except Exception as exc:  # noqa: BLE001 — log everything, fail soft
        print(f"[triage] Claude call failed: {exc}")
        return dict(FALLBACK)
