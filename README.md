# Mahjong Ledger

A Flask web application for recording Mahjong sessions and reviewing yearly performance. Users sign in with Google, manage only their own game records, view dashboard summaries, and submit support reports by email.

## Features

- Google OAuth sign-in
- Per-user session ledger with create, read, update, and delete operations
- Profit, loss, and round summaries by year
- Responsive dashboard
- Optional SendGrid problem-reporting endpoint
- SQLite for local development and PostgreSQL for deployment

## Requirements

- Python 3.10+
- Google OAuth web credentials
- PostgreSQL for production; SQLite is used automatically in local development
- SendGrid credentials only if problem reporting is enabled

## Setup

```bash
git clone https://github.com/mark2146/mahjong-web.git
cd mahjong-web
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Configure the variables documented in `.env.example`. Register the exact callback URL in Google Cloud, for example `http://localhost:5000/auth/google/callback`.

## Run

```bash
python -m backend.run
```

Open <http://127.0.0.1:5000>. A deployment can use:

```bash
gunicorn 'backend.app.main:create_app()'
```

## API overview

| Method | Path | Purpose |
|---|---|---|
| GET | `/auth/google/login` | Start Google sign-in |
| GET | `/api/sessions` | List the current user's sessions |
| POST | `/api/sessions` | Create a session |
| GET/PUT/DELETE | `/api/sessions/<id>` | Read, update, or delete one session |
| GET | `/api/sessions/summary?year=YYYY` | Aggregate annual statistics |
| POST | `/api/report` | Send a problem report |

## Security notes

- Never commit OAuth, database, SendGrid, or Flask secrets.
- Use a long random `FLASK_SECRET_KEY`; development fallbacks are not suitable for production.
- Restrict OAuth redirect URIs and require HTTPS in production.
- The current state-changing endpoints rely on session cookies and should add explicit CSRF protection before an Internet-facing deployment.
- Add rate limiting to login and report endpoints, and avoid returning upstream OAuth error payloads to clients.
- Local SQLite databases are runtime data and must not be committed.

## Project structure

```text
backend/run.py                 local entry point
backend/app/main.py            application factory and configuration
backend/app/api/               auth, session, health, and report routes
backend/app/models/            SQLAlchemy models
backend/app/templates/         server-rendered pages
backend/app/static/            frontend assets
database/                      schema and database support files
```

## Status

Portfolio/demo application. Review the security notes before production use.
