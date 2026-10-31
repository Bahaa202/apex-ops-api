# Decision memo

## Scope and assumptions

- The API is a small FastAPI service written for this assessment, with
  synthetic data only. No Apex systems, credentials or paid cloud
  resources were used.
- "Deploy" means Docker Compose on a single host (local machine and the
  CI runner). There is no cloud target.
- Single replica, single database, no migrations.

## Key decisions and trade-offs

| Decision | Why | Trade-off |
| --- | --- | --- |
| Multi-stage image, non-root uid 10001 | Smaller image, no build tools at runtime, limited blast radius | Slightly longer Dockerfile |
| Separate `/health` and `/ready` | Liveness must not depend on the database, readiness must | Two endpoints to maintain |
| Image tag = version or git SHA, never `latest` | Every release is traceable and can be rolled back | Tags must be managed |
| Rollback by switching back to the previous tag | Simple, fast, executable | Does not undo database changes |
| `needs` between test, build and deploy | A failing test blocks the release | Slower pipeline |
| Trivy fails only on CRITICAL with a fix | Pipeline stays actionable | Lower severities are not blocking |
| Trivy run from its Docker image | The first attempt with a third-party action failed to resolve its tag, and this removes one dependency | Pinned version must be updated manually |
| Alerts written as a proposal | The task asked for a proposal, not a monitoring stack | Rules were not tested on live Prometheus |
| Metrics labelled by route template | Avoids unbounded label cardinality | Raw paths are only in the logs |

## Known limitations

- The deploy job rebuilds the image instead of reusing the scanned one.
- A failed release causes about a minute of downtime (recreate strategy).
- No backups, no dependency audit tool, no live monitoring.
- The CI deploy only proves the stack starts on a throwaway runner.
