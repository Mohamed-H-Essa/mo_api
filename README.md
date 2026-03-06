# Bookmarks API

> **This is a sample/sandbox project** — a deliberately simple API designed as a playground for trying out infrastructure tooling, deployment pipelines, containerization, CI/CD, and other DevOps practices. The application itself (a bookmarks manager) is intentionally minimal so you can focus on the infrastructure around it.

A RESTful API for saving and organizing bookmarks into collections. Built with FastAPI, SQLAlchemy (async), and PostgreSQL.

## Tech Stack

- **Framework:** FastAPI
- **ORM:** SQLAlchemy 2.0 (async)
- **Database:** PostgreSQL 16
- **Migrations:** Alembic
- **Validation:** Pydantic v2
- **Async Driver:** asyncpg
- **Containerization:** Docker & Docker Compose

## Project Structure

```
mo_api/
├── main.py                  # App entrypoint, exception handlers, health check
├── database.py              # Async engine & session setup
├── models.py                # SQLAlchemy ORM models (Collection, Bookmark)
├── schemas.py               # Pydantic request/response schemas
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
├── Dockerfile               # Container image definition
├── docker-compose.yml       # App + PostgreSQL orchestration
├── alembic.ini              # Alembic configuration
├── alembic/
│   ├── env.py               # Migration environment (async-aware)
│   └── versions/
│       └── 001_initial.py   # Initial schema migration
├── routers/
│   ├── collections.py       # CRUD endpoints for collections
│   └── bookmarks.py         # CRUD endpoints for bookmarks
└── GUIDE.md                 # Detailed walkthrough (great for Node.js devs)
```

## Getting Started

### Option 1: Docker Compose (recommended)

This is the fastest way to get everything running — no local Python or PostgreSQL needed.

```bash
# Start the app and database
docker compose up --build

# Run in the background
docker compose up --build -d

# View logs
docker compose logs -f app

# Stop everything
docker compose down

# Stop and delete all data
docker compose down -v
```

The app will be available at `http://localhost:8000`.

### Option 2: Run Locally

Requires Python 3.12+ and a running PostgreSQL instance.

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure the database connection
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 4. Run database migrations
alembic upgrade head

# 5. Start the development server
uvicorn main:app --reload
```

## API Endpoints

### Health

| Method | Path      | Description            |
|--------|-----------|------------------------|
| GET    | `/health` | Health check (includes DB status) |

### Collections

| Method | Path                  | Description       |
|--------|-----------------------|-------------------|
| POST   | `/collections`        | Create collection |
| GET    | `/collections`        | List collections (paginated: `?skip=0&limit=20`) |
| GET    | `/collections/{id}`   | Get collection    |
| PATCH  | `/collections/{id}`   | Update collection |
| DELETE | `/collections/{id}`   | Delete collection (cascades to bookmarks) |

### Bookmarks

| Method | Path                                       | Description              |
|--------|---------------------------------------------|--------------------------|
| POST   | `/collections/{collection_id}/bookmarks`    | Create bookmark          |
| GET    | `/collections/{collection_id}/bookmarks`    | List bookmarks in collection (paginated) |
| GET    | `/bookmarks/{id}`                           | Get bookmark             |
| PATCH  | `/bookmarks/{id}`                           | Update bookmark          |
| DELETE | `/bookmarks/{id}`                           | Delete bookmark          |

### Interactive Docs

FastAPI auto-generates interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Environment Variables

| Variable       | Description                | Default                                                    |
|----------------|----------------------------|------------------------------------------------------------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:password@localhost:5432/bookmarks` |

See `.env.example` for the template.

## Database Migrations

Migrations are managed with Alembic. When running via Docker, migrations execute automatically on startup.

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Generate a new migration (after modifying models.py)
alembic revision --autogenerate -m "description of change"
```

## Use It as Your Infrastructure Sandbox

This project is meant to be a starting point for experimenting with:

- **Containerization** — Tweak the Dockerfile, try multi-stage builds, optimize image size
- **Orchestration** — Expand `docker-compose.yml`, add nginx, redis, or other services
- **CI/CD** — Set up GitHub Actions, GitLab CI, or any pipeline to build, test, and deploy
- **Cloud deployment** — Deploy to AWS (ECS, EKS), GCP (Cloud Run), Azure, fly.io, Railway, etc.
- **Infrastructure as Code** — Wrap it with Terraform, Pulumi, or CloudFormation
- **Monitoring & observability** — Add Prometheus metrics, Grafana dashboards, structured logging
- **Reverse proxies & load balancing** — Put it behind nginx, Traefik, or Caddy
- **Kubernetes** — Write manifests, Helm charts, or Kustomize overlays

The API is simple enough to not get in the way, but complete enough to be a realistic workload (async I/O, database connections, migrations, health checks).

## License

This project is provided as-is for learning and experimentation purposes.
