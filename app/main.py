"""Patchworkz — FastAPI application.

Routes:
  GET  /                  -> frontend
  POST /api/tickets       -> submit a ticket (AI triage runs here, public)
  GET  /api/tickets       -> list all tickets (agent-only)
  GET  /api/tickets/{id}  -> single ticket (agent-only)
  PATCH /api/tickets/{id} -> update ticket status (agent-only)
  GET  /api/tickets/stats -> ticket counts for the dashboard (agent-only)
  POST /api/auth/register -> create an agent account
  POST /api/auth/login    -> exchange credentials for a JWT
"""

from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field

from app import auth, database
from app.claude_service import triage_ticket

app = FastAPI(title="Patchworkz", version="0.1.0")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"


@app.on_event("startup")
def startup() -> None:
    database.init_db()


class TicketIn(BaseModel):
    requester_name: str = Field(min_length=1, max_length=100)
    requester_email: EmailStr
    subject: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=5000)


class StatusUpdate(BaseModel):
    status: str


class AgentIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=200)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.post("/api/auth/register", status_code=201)
def register(agent: AgentIn) -> dict:
    if database.get_agent_by_username(agent.username) is not None:
        raise HTTPException(status_code=409, detail="Username already taken")
    created = database.create_agent(agent.username, auth.hash_password(agent.password))
    return {"id": created["id"], "username": created["username"]}


@app.post("/api/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    agent = auth.authenticate_agent(form_data.username, form_data.password)
    if agent is None:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return Token(access_token=auth.create_access_token(agent["username"]))


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
def get_tickets(agent: dict = Depends(auth.get_current_agent)) -> list[dict]:
    return database.list_tickets()


@app.get("/api/tickets/stats")
def get_stats(agent: dict = Depends(auth.get_current_agent)) -> dict:
    return database.ticket_stats()


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: int, agent: dict = Depends(auth.get_current_agent)) -> dict:
    ticket = database.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.patch("/api/tickets/{ticket_id}")
def update_status(
    ticket_id: int,
    body: StatusUpdate,
    agent: dict = Depends(auth.get_current_agent),
) -> dict:
    if body.status not in database.VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status")
    ticket = database.update_ticket_status(ticket_id, body.status)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
