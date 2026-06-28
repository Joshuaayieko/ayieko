# Orbes — Your AI Assistant 🪐

Orbes is a multi-modal, multi-agent AI assistant with a Python (FastAPI) backend
and a Flutter mobile app. It supports conversational chat backed by an LLM,
long-term + semantic memory, web research, coding help, planning, and a pluggable
tool system (alarms, music, weather, code runner, and more).

```
                  ORBES AI ASSISTANT

      ┌───────────────────────────────────────┐
      │          Mobile App (Flutter)         │
      └───────────────────────────────────────┘
                     │  Voice / Text / Camera
                     ▼
                AI Brain (LLM)
                     │
     ┌───────────────┼──────────────────┐
   Memory       Planner Agent       Tool Manager
     │               │                  │
     └───────────────┼──────────────────┘
                     ▼
   Spotify · Alarm · Calendar · Browser · Search · Code Runner · Weather …
```

## Project structure

```
Orbes/
├── backend/              # FastAPI backend (the "AI brain")
│   ├── app/
│   │   ├── main.py       # App entrypoint + router wiring
│   │   ├── config.py     # Settings loaded from environment
│   │   ├── database.py   # SQLAlchemy engine/session
│   │   ├── models.py     # ORM models (users, conversations, memories…)
│   │   ├── schemas.py    # Pydantic request/response models
│   │   ├── auth.py       # JWT auth + password hashing
│   │   ├── seed.py       # Seeds the admin account on startup
│   │   ├── llm.py        # LLM client (Anthropic Claude)
│   │   ├── agents/       # planner / coding / research / vision / voice
│   │   ├── memory/       # semantic + structured memory store
│   │   ├── tools/        # pluggable tools + registry
│   │   └── routers/      # auth / chat / memory / tools HTTP routes
│   └── requirements.txt
│
├── mobile_app/
│   └── flutter/          # Flutter client (Android + iOS)
│
├── .env.example          # Copy to .env and fill in your secrets
└── README.md
```

## Quick start (backend)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# configure secrets
cp ../.env.example ../.env      # then edit ../.env

uvicorn app.main:app --reload
```

The API is then available at `http://localhost:8000` and interactive docs at
`http://localhost:8000/docs`.

### Admin account

The admin account is seeded automatically on first startup from environment
variables (`ORBES_ADMIN_EMAIL` / `ORBES_ADMIN_PASSWORD`). Set these in your
`.env` file — they are **never** committed to git. The password is stored only
as a bcrypt hash.

## Quick start (mobile app)

```bash
cd mobile_app/flutter
flutter pub get
flutter run            # point API_BASE_URL at your backend
```

## Roadmap

| Version | Focus                                                              | Status |
|---------|-------------------------------------------------------------------|--------|
| v1      | Chat with an LLM, memory, modern interface                        | ✅ scaffolded |
| v2      | Voice conversations + internet search                             | 🚧 in progress |
| v3      | Phone automation (open apps, alarms, timers, notifications)       | 🔌 tool stubs |
| v4      | Vision, document understanding, coding assistance                 | 🔌 agent stubs |
| v5      | Autonomous planning, multi-agent workflows                        | 🧠 planner core |

## Security notes

- Secrets (API keys, admin password) live in `.env`, which is git-ignored.
- Passwords are hashed with bcrypt; auth uses short-lived JWT access tokens.
- The code runner is sandbox-oriented — do not expose it publicly without
  hardening (containerization, resource limits, network isolation).
