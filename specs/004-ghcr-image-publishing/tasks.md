---
description: "Dependency-ordered implementation tasks for GHCR image publishing"
---

# Tasks: GHCR Image Publishing

**Input**: Design documents from `specs/004-ghcr-image-publishing/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/ci.md`, and `quickstart.md`

**Organization**: Tasks are grouped by the user stories in `spec.md`. No application tests or dependencies are added; validation uses the planned workflow lint, Docker build, and registry checks.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: The task can run in parallel because it changes a separate file and has no dependency on unfinished tasks.
- **[Story]**: Maps a task to a spec user story; setup, foundational, and polish tasks omit this label.
- Every task names the exact file or artifact it changes or validates.

## Phase 1: Setup

**Purpose**: Repository initialization and project structure.

No setup changes are needed: the repository already has GitHub Actions workflows and an existing Dockerfile.

## Phase 2: Foundational

**Purpose**: Shared prerequisites that block user story work.

No foundational code changes are needed. The workflow and documentation work can start directly from the approved design.

## Phase 3: User Story 1 - Validate container changes before merge (Priority: P1) 🎯 MVP

**Goal**: Validate builds for pull requests targeting `main`, without package-write permission or publication.

**Independent Test**: A PR targeting `main` reports a successful Docker build for a valid Dockerfile; a deliberately failing build reports failure; no PR image is published.

### Implementation

- [X] T001 [US1] Create `.github/workflows/container-image.yml` with `pull_request` restricted to `main`, `push` restricted to `main`, workflow default `contents: read`, and a PR validation job that checks out with persisted credentials disabled and builds the existing `Dockerfile` with push disabled using full-SHA-pinned actions from `specs/004-ghcr-image-publishing/research.md`.
- [ ] T002 [US1] Validate the pull-request build path in `.github/workflows/container-image.yml` by running the workflow on a PR targeting `main`, confirming the valid build passes, a controlled invalid Dockerfile build fails visibly, and neither run publishes a PR image; follow `specs/004-ghcr-image-publishing/quickstart.md`.

**Checkpoint**: PR builds are visible and cannot publish or obtain package-write permission.

## Phase 4: User Story 2 - Publish reviewed main revisions (Priority: P1)

**Goal**: Publish each successful main revision under its full source commit SHA and `latest`.

**Independent Test**: A successful main push publishes `ghcr.io/mtak/opsgenie-google-calendar-sync:<full-source-commit-sha>` and `:latest`; after the package is public, an anonymous pull of the SHA reference succeeds.

### Implementation

- [X] T003 [US2] Add a publisher job to `.github/workflows/container-image.yml` that runs only on pushes to `main`, uses only `contents: read` and `packages: write`, logs in with the built-in `GITHUB_TOKEN`, generates an OCI source label and exact full-SHA plus `latest` tags, and pushes the existing Dockerfile build using full-SHA-pinned actions and readable version comments from `specs/004-ghcr-image-publishing/research.md`.

**Checkpoint**: Main pushes publish the two required tags; build or registry failures fail the publisher job.

## Phase 5: User Story 3 - Set up public package access (Priority: P2)

**Goal**: Give maintainers clear one-time package setup instructions and deployment tag guidance.

**Independent Test**: A maintainer follows the README steps to connect an existing unlinked package if needed and set GHCR visibility to Public; the README directs deployment users to a selected full-SHA tag and labels `latest` as convenience-only.

### Implementation

- [X] T004 [P] [US3] Add a focused GHCR usage section to `README.md` documenting `ghcr.io/mtak/opsgenie-google-calendar-sync`, the one-time package linking/access and Public visibility steps, anonymous pull access, full-SHA deployment references, and convenience-only use of `latest`.

**Checkpoint**: A maintainer can follow the documented setup after the initial image package exists.

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Validate the combined workflow and verify the published image contract.

- [X] T005 Run `actionlint` on `.github/workflows/container-image.yml`, build the image with `docker build -t opsgenie-google-calendar-sync:ci .`, verify the build-only failure path and 40-character SHA/comment/permission/trigger requirements in `.github/workflows/container-image.yml`, and confirm `.github/workflows/quality.yml` is unchanged; use `specs/004-ghcr-image-publishing/quickstart.md`.
- [ ] T006 After the first successful main publication, confirm both required tags exist and anonymously pull `ghcr.io/mtak/opsgenie-google-calendar-sync:<full-source-commit-sha>` after package visibility is Public; follow `specs/004-ghcr-image-publishing/quickstart.md`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No changes required.
- **Foundational (Phase 2)**: No changes required.
- **User Story 1 (Phase 3)**: Starts immediately; T002 follows T001.
- **User Story 2 (Phase 4)**: T003 follows T001 because it extends the same workflow file.
- **User Story 3 (Phase 5)**: T004 can run in parallel with workflow implementation because it changes only `README.md`.
- **Polish (Phase 6)**: T005 follows T001, T003, and T004. T006 follows successful publication and the one-time public package setup.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on another story; it is the MVP build-validation increment.
- **User Story 2 (P1)**: Depends on the workflow file introduced by US1, but does not change its validation-only behavior.
- **User Story 3 (P2)**: Documentation can be written independently; executing the public visibility step and anonymous pull check requires the package created by US2.

### Parallel Opportunities

- T004 (`README.md`) can run in parallel with T001/T003 (`.github/workflows/container-image.yml`) because the files are separate.
- T002 can begin after T001 while README documentation proceeds independently.
- Publisher implementation T003 must not run in parallel with T001 because both edit the same workflow file.

## Parallel Example: User Story 1 and Documentation

```text
Task: T001 Create the PR build workflow in .github/workflows/container-image.yml
Task: T004 Document GHCR setup and image references in README.md
```

## Implementation Strategy

### MVP First (User Story 1)

1. Complete T001 to add read-only pull request build validation.
2. Complete T002 to validate the PR result and no-publish behavior.
3. Stop for review with a visible PR build check before adding publication permissions.

### Incremental Delivery

1. Deliver US1 PR build validation with no registry write permission.
2. Add US2 main-only publishing with SHA and `latest` tags.
3. Add US3 maintainer setup and deployment-reference documentation.
4. Complete T005 and T006 for combined validation and public pull verification.

## Notes

- The existing quality workflow remains intact; T005 verifies this after implementation.
- No application source, runtime behavior, deployment manifest, or long-lived registry secret is in scope.
- T006 requires a successful main publication and maintainer package settings access; it does not authorize changing package visibility as part of implementation.
