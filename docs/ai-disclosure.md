# AI-use disclosure

## Tool used

Claude (Anthropic), through the chat interface, in one long working
session during the 48-hour window.

## What the AI did

- Proposed the overall plan, repository layout and the order of work.
- Wrote the first version of: the API source (`app/`), the tests
  (`tests/`), the Dockerfile, `docker-compose.yml`, the CI workflow,
  `scripts/deploy.sh`, `scripts/rollback.sh`, `docs/alerts.yml`, the
  runbook, the security/cost notes, the architecture diagrams, the
  decision memo and this disclosure.
- Helped troubleshoot: installing Docker Engine on AlmaLinux under WSL,
  git remote and authentication errors, and the CI failure caused by an
  unresolvable Trivy action tag (fixed by running Trivy from its Docker
  image).
- Explained the reasoning behind each step (liveness vs readiness,
  non-root containers, `needs` in CI, rollback by tag).

## What I did myself

- Created the GitHub repository and pushed every commit.
- Ran every command on my own machine and fixed the problems that
  appeared (misplaced project folder, broken pastes, missing Docker).
- Ran the tests, builds, deployments, the failed release, the automatic
  rollback and the database outage, and captured the evidence in
  `evidence/`.
- Opened the pull request with the intentional failing test and confirmed
  that build and deploy were skipped.
- Reviewed the generated files before submitting.

## Limits

- The code, scripts and documents started as AI-generated drafts. I
  verified behavior by running them; I did not write them from scratch.
- The alert rules were not run against a live Prometheus.
