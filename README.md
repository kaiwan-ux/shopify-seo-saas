# Shopify SEO SaaS — Phase 1 Backend

Production-grade backend foundation for an AI-powered Shopify SEO SaaS platform. Built with **Clean Architecture**, **FastAPI**, and **PostgreSQL**.

> **Phase 1 scope:** Authentication, user management, database foundation, Docker deployment. No Shopify integration, MCP, AI agents, or frontend.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.12+ |
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (access + refresh tokens) |
| Password Hashing | Argon2 (via passlib) |
| Logging | Loguru |
| Package Manager | uv |
| Testing | Pytest + httpx |
| Containers | Docker + Docker Compose |

---

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- (Optional) [uv](https://docs.astral.sh/uv/) for local development

### Run with Docker (recommended)

```bash
# 1. Clone and enter the project
cd seo

# 2. Copy environment file and set secrets
cp .env.example .env
# Edit .env — at minimum set JWT_SECRET_KEY:
# openssl rand -hex 32

# 3. Start everything
docker compose up --build
```

The API will be available at:

- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc

Migrations run automatically on startup via the entrypoint script.

---

## Local Development (without Docker)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Start PostgreSQL (or use docker compose up db)
# Update DATABASE_URL in .env to point to localhost

# Run migrations
alembic upgrade head

# Start the dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Project Structure

```
seo/
├── app/
│   ├── api/              # HTTP route handlers (presentation layer)
│   │   └── v1/           # Versioned API endpoints
│   ├── auth/             # JWT and password utilities
│   ├── config/           # Environment settings (Pydantic Settings)
│   ├── core/             # Exceptions, logging setup
│   ├── db/               # Async engine, session factory
│   ├── dependencies/     # FastAPI dependency injection
│   ├── middleware/       # Request logging middleware
│   ├── models/           # SQLAlchemy ORM models
│   ├── repositories/     # Data access layer (repository pattern)
│   ├── schemas/          # Pydantic request/response schemas
│   ├── services/         # Business logic layer
│   ├── utils/            # Shared helpers
│   ├── workers/          # Background workers (Phase 2 placeholder)
│   ├── scheduler/        # Scheduled jobs (Phase 2 placeholder)
│   └── main.py           # Application factory
├── alembic/              # Database migrations
├── tests/                # Pytest test suite
├── scripts/              # Docker entrypoint
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── .env.example
```

### Architecture Layers

```
┌─────────────────────────────────────────┐
│  API (app/api)          Presentation    │
├─────────────────────────────────────────┤
│  Services (app/services)  Business Logic│
├─────────────────────────────────────────┤
│  Repositories (app/repositories)  Data  │
├─────────────────────────────────────────┤
│  Models (app/models)      Persistence   │
└─────────────────────────────────────────┘
```

**Dependency rule:** Outer layers depend on inner layers. Services never import from API. Repositories never import from Services.

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | No | Health + DB connectivity check |
| `GET` | `/api/v1/version` | No | Application version info |
| `POST` | `/api/v1/auth/register` | No | Register a new user |
| `POST` | `/api/v1/auth/login` | No | Login and receive JWT tokens |
| `POST` | `/api/v1/auth/refresh` | No | Refresh access token |
| `GET` | `/api/v1/users/me` | Yes | Get current user profile |

---

## API Usage Examples

### Register

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass1",
    "full_name": "Jane Doe"
  }'
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-07-05T00:00:00Z",
  "updated_at": "2026-07-05T00:00:00Z"
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass1"
  }'
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Get Current User

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

### Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

---

## Database Models

| Model | Table | Description |
|---|---|---|
| `User` | `users` | Application user accounts |
| `Store` | `stores` | Shopify store placeholder (Phase 2) |
| `AppSettings` | `app_settings` | Per-user preferences and settings |

---

## Security

- Passwords hashed with **Argon2** (OWASP recommended)
- JWT access tokens (30 min) + refresh tokens (7 days)
- Input validation via Pydantic v2 on all endpoints
- Password strength requirements enforced at registration
- Secrets loaded exclusively from environment variables
- CORS configured via `CORS_ORIGINS`
- OpenAPI docs disabled in production (`APP_ENV=production`)
- Global exception handlers prevent stack trace leakage

---

## Testing

```bash
# Ensure PostgreSQL is running and create a test database
createdb seo_db_test

# Run tests
pytest -v

# With coverage
pytest --cov=app --cov-report=term-missing
```

---

## Environment Variables

See [`.env.example`](.env.example) for all available configuration options.

| Variable | Required | Description |
|---|---|---|
| `JWT_SECRET_KEY` | Yes | Secret for signing JWT tokens |
| `DATABASE_URL` | Yes | Async PostgreSQL connection string |
| `POSTGRES_*` | Yes | PostgreSQL credentials (Docker) |
| `CORS_ORIGINS` | No | Comma-separated allowed origins |
| `APP_ENV` | No | `development`, `staging`, or `production` |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |

---

## Migrations

```bash
# Apply all migrations
alembic upgrade head

# Create a new migration after model changes
alembic revision --autogenerate -m "describe change"

# Rollback one step
alembic downgrade -1
```

---

## What's Next (Phase 2+)

- ~~Shopify OAuth integration~~ ✅ Phase 2
- ~~Store sync~~ ✅ Phase 2
- ~~MCP server integration~~ ✅ Phase 2
- AI content generation agents (Phase 3)
- SEO analysis engine (Phase 3)
- Frontend dashboard

See [PHASE2.md](PHASE2.md) for Shopify integration and MCP documentation.  
See [PHASE3.md](PHASE3.md) for AI multi-agent infrastructure documentation.

---

## License

Proprietary — All rights reserved.
