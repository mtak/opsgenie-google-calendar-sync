# CI Contract: Container Image Build and Publication

## Workflow Events

| Event | Scope | Required behavior |
|---|---|---|
| `pull_request` | Target branch `main` | Build from the repository `Dockerfile`; do not log in to GHCR or push an image. |
| `push` | Branch `main` | Build and publish the GHCR image with the full source commit SHA tag and `latest`. |

No other event may publish an image. Do not use `pull_request_target` or `workflow_run` for this workflow.

## Image Reference

- Package: `ghcr.io/mtak/opsgenie-google-calendar-sync`
- Commit-specific tag: the full `${{ github.sha }}` value without prefix or truncation.
- Convenience tag: `latest`, updated by successful pushes to `main` only.
- Deployment consumers choose a full SHA reference deliberately; they do not follow `latest`.

## Permission Contract

- Workflow default: `contents: read`.
- PR validation job: `contents: read` only; no registry login step, `packages: write`, or push enabled.
- Main publisher job: `contents: read` and `packages: write` only; authenticate with the built-in `GITHUB_TOKEN`.
- No long-lived token, `id-token: write`, package deletion, or unrelated permission is required.

## Action Pin Contract

Every external action reference uses a 40-character commit SHA followed by a readable `# vX.Y.Z` comment. Pins must be verified from the action's official release repository. Keep `actions/checkout` credentials from persisting after checkout.

## Package Setup Contract

The publisher creates or updates the repository-associated GHCR package. A maintainer performs a one-time visibility update to Public after initial creation. If the package already exists without the repository association or Actions access, connect the package to this repository and grant the workflow access before expecting a push to succeed. Public package pulls work without registry authentication.

## Failure Contract

- If the Docker build fails, the job fails before any image push starts.
- If authentication, package access, or registry publication fails, the publisher job fails and the run is not reported as a successful publication.
- A pull request build failure produces a visible failed validation job and cannot publish.
- The existing quality workflow retains its current triggers and checks unchanged.
