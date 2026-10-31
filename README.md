# Apex Operations API: DevOps assessment

A small FastAPI service with Postgres, packaged with Docker, tested and
released through GitHub Actions, with a versioned release and rollback
procedure. All data is synthetic.

## Requirements

- Docker Engine with the Compose plugin
- Python 3.12 (only to run the tests locally)
- curl

## Run locally

    git clone https://github.com/Bahaa202/apex-ops-api.git
    cd apex-ops-api
    cp .env.example .env
    docker build --build-arg APP_VERSION=1.0.0 -t apex-ops-api:1.0.0 .
    docker compose up -d
    curl localhost:8000/ready
    curl localhost:8000/version

Edit the placeholder password in `.env` before starting if you like.

## Run the tests

    python3 -m venv .venv && source .venv/bin/activate
    pip install -r requirements-dev.txt
    ruff check .
    pytest -v

Expected: 8 passed on `main`.

## Endpoints

| Path | Purpose |
| --- | --- |
| `/health` | Liveness: the process is up |
| `/ready` | Readiness: the database is reachable |
| `/version` | Running version |
| `/metrics` | Prometheus metrics |
| `POST /operations`, `GET /operations/{id}` | Sample resource stored in Postgres |

## Release and rollback

    docker build --build-arg APP_VERSION=1.1.0 -t apex-ops-api:1.1.0 .
    ./scripts/deploy.sh 1.1.0
    ./scripts/rollback.sh

`deploy.sh` rolls back automatically if `/ready` does not pass in 60s.

## Evidence

CI runs (live on GitHub):

| What | Where |
| --- | --- |
| CI runs on `main` (test, build + scan, deploy) | [Actions tab](https://github.com/Bahaa202/apex-ops-api/actions) |
| Intentional failing test blocks build and deploy | [pull request #1](https://github.com/Bahaa202/apex-ops-api/pull/1) |

Terminal logs, captured from real runs (`evidence/`):

| What | File |
| --- | --- |
| Release 1.1.0, previous tag, non-root `uid=10001` | `evidence/release-1.1.0.log` |
| Broken release 1.2.0 and automatic rollback to 1.1.0 | `evidence/rollback-run.log` |
| Failure investigation during the restart loop | `evidence/incident-investigation.log` |
| Database outage: `/health` 200, `/ready` 503, error log | `evidence/incident-db-down.log` |

The pull request is intentionally left unmerged. Its branch
`demo/intentional-failure` contains the failing test; `main` stays green.

## Documentation

- `docs/runbook.md`: deploy, rollback, incident response, troubleshooting
- `docs/architecture.md`: runtime, CI/CD and rollback diagrams
- `docs/decision-memo.md`: assumptions, decisions, trade-offs, limitations
- `docs/security-and-cost.md`: secrets, least privilege, scanning, cloud cost path
- `docs/alerts.yml`: alert rules proposal (not run on a live Prometheus)
- `docs/ai-disclosure.md`: how AI was used
