"""Email notifications for new tickets.

Sends the AI-suggested response to a support inbox as a draft for an agent
to review — it never emails the requester directly. Like claude_service,
a failure here (bad credentials, network) never blocks ticket creation.
"""

import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.environ.get("SMTP_HOST") or "smtp.gmail.com"
SMTP_PORT = int(os.environ.get("SMTP_PORT") or "587")
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_APP_PASSWORD = os.environ.get("SMTP_APP_PASSWORD")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL")


def send_ticket_notification(ticket: dict) -> None:
    if not (SMTP_USERNAME and SMTP_APP_PASSWORD and NOTIFY_EMAIL):
        print("[email] Skipped — SMTP not configured")
        return

    try:
        ticket_id = "TKT-" + str(ticket["id"]).zfill(4)
        suggested = ticket.get("suggested_response") or "(No AI suggestion — needs manual triage.)"
        # Strip CR/LF from user-supplied fields used in headers -- EmailMessage
        # rejects embedded newlines outright, which would otherwise raise here
        # and (since this whole function is best-effort) must never escape.
        safe_subject = ticket["subject"].replace("\r", " ").replace("\n", " ")

        msg = EmailMessage()
        msg["Subject"] = f"[{ticket_id}] {ticket['priority']} · {ticket['category']} — {safe_subject}"
        msg["From"] = SMTP_USERNAME
        msg["To"] = NOTIFY_EMAIL
        msg.set_content(
            f"New ticket {ticket_id} from {ticket['requester_name']} <{ticket['requester_email']}>\n\n"
            f"Subject: {ticket['subject']}\n"
            f"Category: {ticket['category']} · Priority: {ticket['priority']}\n\n"
            f"Description:\n{ticket['description']}\n\n"
            f"--- Suggested first response (draft, review before sending) ---\n{suggested}\n\n"
            f"Triage reasoning: {ticket.get('triage_reasoning') or 'n/a'}\n"
        )

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_APP_PASSWORD)
            server.send_message(msg)
    except Exception as exc:  # noqa: BLE001 — notification is best-effort, must never block ticket creation
        print(f"[email] Notification failed: {exc}")
