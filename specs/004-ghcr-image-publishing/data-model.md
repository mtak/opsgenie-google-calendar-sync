# Data Model: GHCR Image Publishing

This feature adds no application data model. The following CI and registry records define the observable publishing behavior.

## Source Revision Image

- **Source commit**: Full Git commit SHA that triggered a successful main-branch publisher run.
- **Image reference**: `ghcr.io/mtak/opsgenie-google-calendar-sync:<full-source-commit-sha>`.
- **Identity rule**: The tag text is the complete source commit SHA, with no short-SHA truncation or prefix.
- **Lifecycle**: Created only by a successful main push build; retained as the deployable reference for that source revision. The tag is immutable by convention and must not be used as a rolling pointer.

## Convenience Image Tag

- **Image reference**: `ghcr.io/mtak/opsgenie-google-calendar-sync:latest`.
- **Identity rule**: Points to the most recently published successful main build.
- **Lifecycle**: May advance on each successful main publication. Deployments must not track this tag.

## GHCR Package

- **Registry path**: `ghcr.io/mtak/opsgenie-google-calendar-sync`.
- **Repository association**: The OCI source metadata identifies this repository so the package can be linked to the workflow repository.
- **Visibility**: Private by default on first publication; changed once by a package maintainer to Public to permit anonymous pulls.
- **Access**: The publishing job uses workflow `GITHUB_TOKEN` with `packages: write`; no long-lived registry secret is stored.

## Workflow Run

- **Pull request run**: Applies to pull requests targeting `main`; builds the Dockerfile with push disabled and source-read permission only.
- **Main publication run**: Applies to pushes to `main`; builds and pushes both specified tags with source-read and package-write permission.
- **Failure outcome**: A build or publish error fails the corresponding Actions job. A build failure does not begin a registry push. A registry failure cannot be represented as a successful completed publisher job.
