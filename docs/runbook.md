# Runbook: Apex Operations API

## Deploy a new version

1. Build a versioned image (never use `latest`):

        docker build --build-arg APP_VERSION=1.1.0 -t apex-ops-api:1.1.0 .

2. Deploy. The script saves the current tag, switches, waits for `/ready`,
   and rolls back automatically if readiness does not pass within 60s:

        ./scripts/deploy.sh 1.1.0

3. Verify:

        curl -s localhost:8000/version
        docker compose ps

## Rollback (manual)

Reverts to the tag recorded in `.previous_tag` by the last deploy:

        ./scripts/rollback.sh

Notes:
- The database volume is never touched by a rollback.
- If a release ever includes a schema migration, a code-only rollback is
  not enough. This project has no migrations yet.
- Expect about a minute of downtime during a failed release (recreate strategy).

## DB unreachable

Alert: `ApiNotReady`. Symptom: `/health` returns 200, `/ready` returns 503.
The app is alive but cannot reach Postgres, so do NOT restart the app.

1. Confirm the symptom:

        curl -s -o /dev/null -w "%{http_code}\n" localhost:8000/ready

2. Read the error in the structured logs:

        docker compose logs app --tail 20 | grep "readiness failed"

   `Name or service not known` means the db container is missing from the
   network (stopped or removed). `Connection refused` means the container
   exists but Postgres is not accepting connections.

3. Check and recover the database:

        docker compose ps db
        docker compose start db

4. Verify recovery: `/ready` returns 200. Data is kept in the `pgdata` volume.

## Restart loop

Alert: `ApiTargetDown`. Symptom: app status is `Restarting`, `/ready` is
unreachable, often right after a release.

1. Check status and exit code:

        docker compose ps

2. Read the logs. Empty logs together with `Restarting (1)` mean the process
   exits at startup:

        docker compose logs app --tail 20

3. If this started after a deploy, roll back first and investigate after:

        ./scripts/rollback.sh

4. Verify the version and the data:

        curl -s localhost:8000/version
        curl -s localhost:8000/operations/1

## Troubleshooting

| Symptom | Likely cause | Check | Fix |
| --- | --- | --- | --- |
| `/ready` 503, `/health` 200 | DB down or unreachable | `docker compose ps db`, app logs | `docker compose start db` |
| App `Restarting`, empty logs | Process exits at startup (bad image) | `docker compose ps` | `./scripts/rollback.sh` |
| `deploy.sh` says image not found | Tag was never built | `docker images apex-ops-api` | Build the tag, redeploy |
| `rollback.sh`: no previous tag | No deploy ran yet | `cat .previous_tag` | Set `APP_IMAGE_TAG` in `.env`, then `docker compose up -d` |
| Port 8000 in use | Another process on the host | `ss -ltnp \| grep 8000` | Change `APP_PORT` in `.env` |
| Data missing after restart | Volume removed with `down -v` | `docker volume ls` | Restore from backup (none in this demo) |
