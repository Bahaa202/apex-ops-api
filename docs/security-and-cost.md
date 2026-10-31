# Security and cost notes

## Secrets handling

- No secrets in the repo. `.env` is git-ignored; `.env.example` holds
  placeholder values only.
- The local Postgres password is generated with `openssl rand -hex 12`.
- The CI deploy job uses the placeholder values from `.env.example` on a
  throwaway runner. No real credential exists in this project.
- GitGuardian reported no secrets on the pull request.
- In a real environment: a secrets manager (for example AWS Secrets Manager
  or SSM Parameter Store), injected at runtime, never baked into images.

## Least privilege

- Container runs as non-root (uid 10001), verified with `id`.
- Compose sets `read_only: true`, `cap_drop: [ALL]` and
  `no-new-privileges`.
- The database port is not published to the host.
- The CI token is limited to `permissions: contents: read`.
- Known gap: the app container has no writable path, which works here
  because SQLAlchemy only talks to Postgres. An app that writes temp files
  would need a tmpfs mount.

## Scanning

- CI scans the built image with Trivy and fails on CRITICAL findings that
  have a fix available (`--ignore-unfixed`). This is a deliberate
  trade-off: the pipeline should not fail on issues nobody can fix yet.
- Trivy runs from the official Docker image instead of a third-party
  action, which removes one supply-chain dependency.
- Not done: a separate Python dependency audit (for example `pip-audit`).
  It is listed under improvements.

## Cost-aware path to cloud hosting

Principle: start with the cheapest option that keeps the same artifacts
(versioned image, compose file, scripts), and move up only when a real
need appears.

1. Stage 1: one small VM (for example a small EC2 or Lightsail instance)
   running the same Docker Compose stack. Lowest cost and no new concepts.
   Use a container registry (GHCR is free for public images) so the VM
   pulls the exact tag that CI scanned.
2. Stage 2: move Postgres to a managed database when the data matters
   (automated backups, point-in-time recovery). This is the first part
   that is worth paying for.
3. Stage 3: a managed container service (for example ECS on Fargate) when
   one VM becomes a risk or traffic grows. Two tasks behind a load
   balancer allow rolling updates.
4. Cost controls from day one: a billing budget with an alert, small
   instance sizes, log retention limits, and shutting down non-production
   environments outside working hours.
5. Prices change, so re-check current pricing before choosing sizes.

## What I would improve with more time

- Push the scanned image to a registry in CI and deploy that exact image,
  instead of rebuilding it in the deploy job.
- Avoid downtime on release with blue/green or rolling updates.
- Add `pip-audit` for dependency scanning and pin the base image by digest.
- Run Prometheus and Alertmanager and validate `docs/alerts.yml` with
  `promtool` (the rules are a proposal and were not run against a live
  Prometheus).
- Database migrations (Alembic) and a tested backup and restore procedure.
- Make the rollback script migration-aware.
- Real CI deployment target with a protected environment and approval.
