# Patchworkz — AI-Powered IT Ticket Triage

**Live demo: [patchworkz.onrender.com](https://patchworkz.onrender.com)**
(hosted on Render's free tier — the first request after a period of inactivity
can take 30–50s to wake up, and the SQLite database resets on redeploy)

A helpdesk ticket system where Claude automatically categorizes incoming tickets,
assigns a priority, and drafts a suggested first response based on your knowledge base.
Staff log in to view the ticket queue, a live dashboard, and move tickets through
an open → in progress → resolved workflow. New tickets also trigger an email
notification with the AI-drafted reply for an agent to review.

Built with **FastAPI + SQLite + Claude API** and a vanilla HTML/JS frontend.
No build tools required — clone, install, run.

## What it demonstrates (for your resume)

- REST API design (FastAPI, Pydantic validation)
- Database persistence (SQLite)
- LLM integration with structured JSON outputs (Anthropic API)
- JWT authentication (password hashing, protected routes)
- Data visualization (Chart.js dashboard from aggregated API data)
- Email integration (SMTP notifications, graceful degradation on failure)
- Async Python, environment-based config, graceful error handling
- Responsive, light/dark-mode frontend that consumes your own API
- Deployed to a live URL (Render)

## Quick start

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# then edit .env: your Anthropic key, a random JWT secret, and (optionally)
# Gmail SMTP details for email notifications — see comments in .env.example

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
│   ├── auth.py            # JWT + password hashing for staff accounts
│   ├── claude_service.py  # Claude API call + JSON parsing
│   ├── email_service.py   # SMTP notification on new ticket
│   └── knowledge_base.py  # Your IT knowledge base (edit me!)
├── static/
│   └── index.html         # Frontend (form, staff login, dashboard, queue)
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

## Roadmap (shipped)

1. ✅ **Auth** — JWT-based staff accounts, rolled by hand (`auth.py`)
2. ✅ **Dashboard** — ticket volume by category/priority/status (Chart.js)
3. ✅ **Status workflow** — open → in progress → resolved, with an update endpoint
4. ✅ **Email notifications** — AI-suggested response emailed to a support inbox as a draft (smtplib)
5. ✅ **Deploy** — live on [Render's free tier](https://patchworkz.onrender.com)

## Notes

- API docs: https://docs.claude.com/en/api/overview
- The model used is `claude-sonnet-4-6`. You can swap in a cheaper/faster model
  in `claude_service.py` if you're watching costs.
- SQLite file (`tickets.db`) is created automatically on first run.
