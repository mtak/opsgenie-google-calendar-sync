# Implementation Plan: GHCR Image Publishing

**Branch**: `004-ghcr-image-publishing` | **Date**: 2026-11-01 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/004-ghcr-image-publishing/spec.md`

## Summary

Add a separate GitHub Actions workflow that builds the existing Dockerfile on pull requests targeting `main` without publishing, and builds and publishes on pushes to `main`. The main publisher will tag the repository image as `ghcr.io/mtak/opsgenie-google-calendar-sync:<full-commit-sha>` and `:latest`, use only `contents: read` and `packages: write`, and rely on `GITHUB_TOKEN`. A repository documentation section will explain the initial GHCR package linking and public-visibility setup. The existing quality workflow and application runtime remain untouched.

## Technical Context

**Language/Version**: Dockerfile uses `python:3.12-slim`; no application language changes.

**Primary Dependencies**: GitHub Actions; Docker Buildx; official Docker actions for checkout, Buildx setup, GHCR login, image metadata, and build/push. Pin each action to a verified full commit SHA with a readable version comment. Research records candidate pins verified against official release tags.

**Storage**: GHCR stores the published container package; no application data or CI artifact retention is added.

**Testing**: Validate workflow syntax with `actionlint`; inspect trigger, job condition, permissions, and pin policy; build the Dockerfile locally with `docker build`; exercise a deliberately invalid Docker build to check failure reporting; after a successful main publication, inspect both registry tags and anonymously pull the full-SHA image.

**Target Platform**: GitHub Actions on `ubuntu-latest`; GitHub Container Registry (`ghcr.io`); the existing single-platform Dockerfile build.

**Project Type**: Python CLI container image with repository-level CI and documentation.

**Performance Goals**: No separate performance target; retain a single-platform build and avoid matrix expansion.

**Constraints**: Image validation is limited to pull requests targeting `main` and has `contents: read` only. Publication is limited to pushes to `main` and receives `contents: read` plus `packages: write`. Do not use `pull_request_target`, `workflow_run`, long-lived registry credentials, or deployment manifests. Preserve `.github/workflows/quality.yml` and its existing checks without modification. Package visibility requires a one-time GitHub UI action after initial package creation.

**Scale/Scope**: One additional workflow and a README operations section. No application code, runtime behavior, dependency, or deployment changes.

## Constitution Check

- **I. Specification-Driven Development**: PASS. This plan follows the clarified GHCR publishing specification.
- **II. Approval Before Planning and Implementation**: PASS. The user invoked the Plan stage after clarification. Coding remains gated on approval of this plan.
- **III. Small, Reviewable Changes**: PASS. The planned diff is limited to one workflow and a focused documentation update.
- **IV. Automated Verification**: PASS. The plan includes workflow linting and Docker build validation after implementation.
- **V. Repository Guidance Is Authoritative**: PASS. Existing quality automation is preserved; image publishing remains separate.

**Gate result**: PASS. No constitution violations identified.

## Project Structure

### Documentation (this feature)

```text
specs/004-ghcr-image-publishing/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── ci.md
├── quickstart.md
└── tasks.md                 # Generated in the next Spec Kit stage
```

### Source Code (repository root)

```text
.github/workflows/
├── quality.yml              # Existing; retain unchanged
└── container-image.yml      # New build validation and publisher workflow

README.md                    # Add GHCR image reference and one-time public setup
Dockerfile                   # Existing build context; no runtime changes planned
```

**Structure Decision**: Keep image automation in its own workflow so its `packages: write` permission cannot apply to pull request validation and so the quality workflow remains unchanged. Use one read-only PR build job and a separate main-push publisher job. Use the repository's `org.opencontainers.image.source` metadata label so GHCR can associate the package with this repository for workflow access; generate the label from image metadata rather than hard-coding repository details into application runtime configuration.

## Phase 0: Research Findings

See [research.md](research.md). Official GitHub guidance supports `contents: read` and `packages: write` for package publication and confirms that public GHCR container packages allow anonymous pulls. The GHCR package starts private, so documentation must include the maintainer's one-time visibility change. The metadata action can produce a full-length SHA tag and OCI source label. Exact action commit pins and source references are recorded in the research artifact.

## Phase 1: Design

- [Data model](data-model.md) describes the image tags, package visibility, and workflow outcomes; it introduces no application entities.
- [CI contract](contracts/ci.md) defines triggers, job-level permission separation, tag names, and failure behavior.
- [Quickstart](quickstart.md) defines local workflow and Docker build validation and the post-publication anonymous pull check.

## Constitution Check (Post-Design)

- **I. Specification-Driven Development**: PASS. Requirements map to the clarified spec and CI contract.
- **II. Approval Before Planning and Implementation**: PASS. This plan is ready for review; implementation has not started and remains gated on approval.
- **III. Small, Reviewable Changes**: PASS. No Dockerfile runtime, application, or deployment change is needed.
- **IV. Automated Verification**: PASS. The quickstart covers workflow linting, permission/tag review, local Docker build, and registry smoke validation.
- **V. Repository Guidance Is Authoritative**: PASS. The existing quality checks remain unchanged and the feature stays within the approved spec.

**Post-design gate result**: PASS.

## Complexity Tracking

No constitution violations. Separate validation and publication jobs are needed to keep package-write permission out of all pull request runs while satisfying publication on main.
