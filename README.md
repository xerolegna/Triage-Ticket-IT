# TriageDesk — AI-Powered IT Ticket Triage

A helpdesk ticket system where Claude automatically categorizes incoming tickets,
assigns a priority, and drafts a suggested first response based on your knowledge base.

Built with **FastAPI + SQLite + Claude API** and a vanilla HTML/JS frontend.
No build tools required — clone, install, run.

## What it demonstrates (for your resume)

- REST API design (FastAPI, Pydantic validation)
- Database persistence (SQLite)
- LLM integration with structured JSON outputs (Anthropic API)
- Async Python, environment-based config, graceful error handling
- A working frontend that consumes your own API

## Quick start

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your API key
cp .env.example .env
# then edit .env and paste your key from https://console.anthropic.com

# 4. Run it
uvicorn app.main:app --reload
```

Open http://localhost:8000 — submit a ticket and watch Claude triage it.

Interactive API docs (free with FastAPI): http://localhost:8000/docs

## Project structure

```
ticket-triage/
├── app/
│   ├── main.py            # FastAPI app + routes
│   ├── database.py        # SQLite helpers
│   ├── claude_service.py  # Claude API call + JSON parsing
│   └── knowledge_base.py  # Your IT knowledge base (edit me!)
├── static/
│   └── index.html         # Frontend (form + live ticket board)
├── requirements.txt
├── .env.example
└── README.md
```

## How the AI triage works

When a ticket is submitted, `claude_service.py` sends the subject + description
to Claude along with your knowledge base, and asks for **JSON only**:

```json
{
  "category": "network",
  "priority": "P2",
  "suggested_response": "Hi Sarah, it sounds like...",
  "reasoning": "VPN outage affecting one user..."
}
```

The response is validated and stored with the ticket. If the API call fails,
the ticket is still saved with category `unclassified` — the system degrades
gracefully instead of crashing.

## Roadmap (build these next, one per week)

1. **Auth** — add user accounts with JWT (fastapi-users or roll your own)
2. **Dashboard** — ticket volume by category/priority (Chart.js)
3. **Status workflow** — open → in progress → resolved, with an update endpoint
4. **Email notifications** — send the suggested response as a draft (smtplib)
5. **Deploy** — Render or Railway free tier, then put the live URL on your resume

## Notes

- API docs: https://docs.claude.com/en/api/overview
- The model used is `claude-sonnet-4-6`. You can swap in a cheaper/faster model
  in `claude_service.py` if you're watching costs.
- SQLite file (`tickets.db`) is created automatically on first run.
