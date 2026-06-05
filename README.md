# Real-Time Analytics Platform

A full-stack real-time analytics platform with event ingestion, dashboards, alerting, scheduled PDF reports, and WebSocket notifications.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Network                           │
│                                                                 │
│   ┌───────────┐     ┌───────────┐     ┌────────────────────┐   │
│   │  Frontend  │────▶│  Backend   │────▶│    PostgreSQL 16   │   │
│   │  Next.js  │     │  FastAPI   │     └────────────────────┘   │
│   │  :3000    │     │  :8000    │                               │
│   └───────────┘     │           │     ┌────────────────────┐   │
│                     │  /health  │────▶│     Redis 7        │   │
│                     │  /api/v1  │     │  (broker + cache)  │   │
│                     └─────┬─────┘     └────────┬───────────┘   │
│                           │                    │               │
│                     ┌─────▼─────┐     ┌────────▼───────────┐   │
│                     │  Celery   │     │   Celery Beat      │   │
│                     │  Worker   │     │  (cron scheduler)  │   │
│                     └───────────┘     └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Service responsibilities

| Service | Role |
|---|---|
| **frontend** | Next.js 16 SPA — dashboards, alerts, reports UI |
| **backend** | FastAPI — REST API, WebSocket gateway, JWT auth |
| **postgres** | Primary datastore — events, dashboards, alerts, reports |
| **redis** | Celery broker + result backend, pub/sub for real-time WS |
| **celery-worker** | Executes background tasks (PDF generation, alert evaluation) |
| **celery-beat** | Dispatches scheduled tasks (daily/weekly/monthly reports, alert polling) |

---

## Quick Start

### Prerequisites

- Docker ≥ 24 and Docker Compose v2
- GNU Make (optional but handy)

### 1 — Clone and configure environment

```bash
git clone <repo-url>
cd real-time-analytics
cp .env.example .env
```

Open `.env` and update at minimum:

- `POSTGRES_PASSWORD` — use a strong password
- `JWT_SECRET_KEY` — generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- `DATABASE_URL` — ensure it matches `POSTGRES_USER`/`POSTGRES_PASSWORD`/`POSTGRES_DB`

### 2 — Start all services

```bash
docker compose up --build -d
```

Migrations run automatically when the backend starts.

### 3 — Verify

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/api/docs

# Frontend
open http://localhost:3000
```

---

## Local Development (without Docker)

### Backend

```bash
cd apps/backend
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"

# Start Postgres and Redis (Docker or local)
docker compose up postgres redis -d

# Apply migrations
alembic upgrade head

# Run API server
uvicorn src.main:app --reload

# Run Celery worker (separate terminal)
celery -A src.celery_app.celery_app worker --loglevel=info

# Run Celery beat (separate terminal)
celery -A src.celery_app.celery_app beat --loglevel=info
```

### Frontend

```bash
cd apps/frontend
npm install
npm run dev          # http://localhost:3000
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@postgres:5432/analytics_db` | Async PostgreSQL DSN |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |
| `JWT_SECRET_KEY` | — | **Required in production.** HS256 signing key |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `30` | Refresh token TTL |
| `ENVIRONMENT` | `production` | `production` enables JSON logs and validates JWT secret |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |
| `REPORTS_DIR` | `/app/reports` | Directory for generated PDF reports |
| `UVICORN_WORKERS` | `2` | Uvicorn worker count |
| `CELERY_CONCURRENCY` | `4` | Celery worker concurrency |
| `LOG_LEVEL` | `info` | Log level for uvicorn / celery |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend URL visible to the browser |
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_DB` | `analytics_db` | PostgreSQL database name |

---

## API Reference

Interactive docs are available at `/api/docs` (Swagger UI) and `/api/redoc`.

### Auth

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new organization + owner |
| `POST` | `/api/v1/auth/login` | Obtain JWT tokens |
| `POST` | `/api/v1/auth/refresh` | Refresh access token |

### Events

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/events` | Ingest an event (API key auth) |
| `GET` | `/api/v1/events` | List events |

### Dashboards & Widgets

| Method | Path | Description |
|---|---|---|
| `GET/POST` | `/api/v1/dashboards` | List / create dashboards |
| `GET/PATCH/DELETE` | `/api/v1/dashboards/{id}` | Read / update / delete |
| `GET/POST` | `/api/v1/dashboards/{id}/widgets` | List / create widgets |

### Alerts

| Method | Path | Description |
|---|---|---|
| `GET/POST` | `/api/v1/alerts` | List / create alerts |
| `GET/PATCH/DELETE` | `/api/v1/alerts/{id}` | Read / update / delete |

### Reports

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/reports` | Create a scheduled report (triggers initial PDF immediately) |
| `GET` | `/api/v1/reports` | List reports |
| `GET` | `/api/v1/reports/{id}` | Get a single report |

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns `{"status","database","redis"}` — 200 ok / 503 degraded |

### WebSocket

Connect to `ws://host/api/v1/ws/{org_id}?token=<access_token>` to receive real-time alert notifications.

---

## Observability

### Structured Logs

In `ENVIRONMENT=production` the backend emits JSON logs to stdout:

```json
{
  "timestamp": "2026-06-06T12:00:00",
  "level": "INFO",
  "logger": "src.api.routes.health",
  "correlation_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "message": "Health check passed."
}
```

In development, human-readable text format is used instead.

### Correlation IDs

Every request receives an `X-Correlation-ID` response header. Pass the header on incoming requests to propagate your own ID (useful for tracing across services).

### Health Check

`GET /health` performs live connectivity checks against PostgreSQL and Redis. Returns 200 when all dependencies are healthy, 503 when any are unreachable.

---

## CI / CD

GitHub Actions workflow at [.github/workflows/ci.yml](.github/workflows/ci.yml) runs on every push and pull request to `main` / `develop`:

```
backend-lint  ──┐
                ├── backend-test ──┐
frontend-build ─┘                 ├── docker-build
                                  │
                                  └── (push images if desired)
```

| Job | What it does |
|---|---|
| **backend-lint** | Ruff (lint + format) and Black format check |
| **backend-test** | Pytest against real Postgres + Redis CI services; runs Alembic migrations |
| **frontend-build** | TypeScript type-check, ESLint, `next build` |
| **docker-build** | Builds both images with layer caching (smoke-test, no push) |

To enable image pushing, add Docker registry credentials to repository secrets and update the `push:` flag and `tags:` in the workflow.

---

## Database Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Create a new migration
alembic revision --autogenerate -m "describe the change"

# Downgrade one step
alembic downgrade -1
```

Migrations run automatically on backend container startup.

---

## Scheduled Reports

Reports are generated as PDFs using ReportLab and stored in the `reports/` volume.

**Celery Beat schedule:**

| Frequency | Cron | Task |
|---|---|---|
| `DAILY` | `0 0 * * *` | Generates a report for the last 24 hours |
| `WEEKLY` | `0 0 * * 1` | Generates a report for the last 7 days |
| `MONTHLY` | `0 0 1 * *` | Generates a report for the last 30 days |

An initial PDF is also triggered immediately when a report is created via `POST /api/v1/reports`.

---

## Project Structure

```
.
├── .env.example                    # Template — copy to .env
├── .github/workflows/ci.yml        # GitHub Actions CI pipeline
├── docker-compose.yml              # All six services
├── apps/
│   ├── backend/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml          # Dependencies, Ruff, Black, Pytest config
│   │   ├── alembic/                # Database migrations
│   │   ├── src/
│   │   │   ├── api/
│   │   │   │   ├── routes/         # FastAPI route handlers
│   │   │   │   └── dependencies.py # DI factories
│   │   │   ├── core/
│   │   │   │   ├── config.py       # Settings (env vars)
│   │   │   │   └── logging.py      # Structured logging + correlation ID
│   │   │   ├── middleware/
│   │   │   │   └── correlation_id.py
│   │   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── repositories/       # Data access layer
│   │   │   ├── schemas/            # Pydantic request/response schemas
│   │   │   ├── services/           # Business logic
│   │   │   └── tasks/              # Celery tasks
│   │   └── tests/
│   │       ├── conftest.py
│   │       └── test_health.py
│   └── frontend/
│       ├── Dockerfile
│       ├── next.config.ts
│       └── app/                    # Next.js App Router pages
└── README.md
```
