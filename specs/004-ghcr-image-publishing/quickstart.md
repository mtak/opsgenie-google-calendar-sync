# Quickstart: Validate GHCR Image Publishing

## Prerequisites

- Docker Engine with Buildx support for local image builds.
- `actionlint` for GitHub Actions workflow validation.
- GitHub access to the repository and GHCR package page for post-publication checks.

## Local Docker Build

From the repository root:

```sh
docker build -t opsgenie-google-calendar-sync:ci .
```

Expected result: the existing Dockerfile builds successfully and the image is available locally as `opsgenie-google-calendar-sync:ci`.

To check build failure handling without touching the real Dockerfile, create a temporary invalid Dockerfile and build it:

```sh
printf 'FROM invalid.example.invalid/no-such-image:never\n' > /tmp/Dockerfile.invalid
docker build -f /tmp/Dockerfile.invalid -t opsgenie-google-calendar-sync:invalid .
```

Expected result: Docker exits non-zero. The CI build step must likewise report failure; it must not continue to a push step.

## Workflow Validation

```sh
actionlint .github/workflows/container-image.yml
```

Then inspect the workflow contract:

- PR trigger is restricted to pull requests targeting `main`.
- Push trigger is restricted to `main`.
- PR validation has `contents: read`, does not log in to GHCR, and configures the build with push disabled.
- The publisher runs only for a main push and has only `contents: read` and `packages: write`.
- Every external action has a verified 40-character SHA and readable version comment.
- `quality.yml` remains unchanged.

## GitHub Package Setup (One Time)

After the first successful main publication creates the package, open the package under the repository owner's **Packages** tab. In the package's **Package settings**, change visibility from Private to **Public**. If a package with the same name already exists, connect it to this repository and grant this repository's Actions workflow access before relying on `GITHUB_TOKEN` publication.

## Post-Publication Check

After a push to `main` completes successfully:

1. Confirm the package contains both `latest` and the full source commit SHA shown by the workflow run.
2. Pull the commit-specific image without logging in:

   ```sh
   docker pull ghcr.io/mtak/opsgenie-google-calendar-sync:<full-source-commit-sha>
   ```

3. Confirm the anonymous pull succeeds after package visibility is Public.
4. Treat the full-SHA tag as the deployment reference. `latest` is for convenience and is not a deployment target.

A build or publication error must leave the Actions run failed. Do not infer publication success from a partially updated registry tag list if the publishing job failed.
