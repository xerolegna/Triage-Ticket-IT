"""TriageDesk — FastAPI application.

Routes:
  GET  /              -> frontend
  POST /api/tickets   -> submit a ticket (AI triage runs here)
  GET  /api/tickets   -> list all tickets
  GET  /api/tickets/{id} -> single ticket
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from app import database
from app.claude_service import triage_ticket

app = FastAPI(title="TriageDesk", version="0.1.0")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.on_event("startup")
def startup() -> None:
    database.init_db()


class TicketIn(BaseModel):
    requester_name: str = Field(min_length=1, max_length=100)
    requester_email: EmailStr
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=5000)


@app.post("/api/tickets", status_code=201)
def create_ticket(ticket: TicketIn) -> dict:
    triage = triage_ticket(
        ticket.requester_name, ticket.subject, ticket.description
    )
    return database.insert_ticket(
        requester_name=ticket.requester_name,
        requester_email=ticket.requester_email,
        subject=ticket.subject,
        description=ticket.description,
        category=triage["category"],
        priority=triage["priority"],
        suggested_response=triage["suggested_response"],
        triage_reasoning=triage["reasoning"],
    )


@app.get("/api/tickets")
def get_tickets() -> list[dict]:
    return database.list_tickets()


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: int) -> dict:
    ticket = database.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
