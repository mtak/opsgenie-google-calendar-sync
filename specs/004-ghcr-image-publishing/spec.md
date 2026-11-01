# Feature Specification: GHCR Image Publishing

**Feature Branch**: `004-ghcr-image-publishing`

**Created**: 2026-11-01

**Status**: Draft

**Input**: User description: "Add CI to build and publish this repository’s container image to GitHub Container Registry (GHCR). Validate image builds on pull requests without publishing, publish a full source commit SHA tag and latest on main, use GITHUB_TOKEN with least privilege and pinned third-party actions, preserve quality checks, and document one-time public package setup."

## Clarifications

### Session 2026-11-01

- Q: Should image build validation run for pull requests targeting any branch, or only pull requests targeting `main`? → A: Only pull requests targeting `main`; other pull request target branches are out of scope for image build validation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validate container changes before merge (Priority: P1)

A contributor opens or updates a pull request and can see whether the repository's container image builds successfully, without any image being published from that pull request.

**Why this priority**: Build failures should be found during review while ensuring unreviewed pull request code cannot publish a registry package.

**Independent Test**: Open a pull request with a valid Dockerfile change and confirm the image build check passes and no image tag is published. Introduce an invalid Docker build input and confirm the check fails.

**Acceptance Scenarios**:

1. **Given** a pull request targets `main`, **When** the image workflow completes, **Then** the image is built from the repository Dockerfile and the build result is visible on the pull request.
2. **Given** a pull request build succeeds, **When** the registry package is inspected, **Then** no image from that pull request has been published.
3. **Given** a pull request image build fails, **When** its workflow completes, **Then** the build check reports failure and the workflow does not publish an image.

### User Story 2 - Publish reviewed main revisions (Priority: P1)

A maintainer merges a change to `main` and can retrieve the image corresponding to that exact source revision from the public GHCR package.

**Why this priority**: Deployment changes must be able to select and deliberately pin an image built from a known source commit.

**Independent Test**: Push a revision to `main`, confirm the workflow publishes the package tags for that revision, and pull the full-SHA-tagged image anonymously.

**Acceptance Scenarios**:

1. **Given** a commit is pushed to `main`, **When** its image build succeeds, **Then** GHCR contains the repository image tagged with that commit's full source SHA and `latest`.
2. **Given** a user knows a published full source SHA tag, **When** they pull that image without authenticating, **Then** the pull succeeds because the package is public.
3. **Given** a deployment is updated to a full source SHA tag, **When** later main revisions are published, **Then** the selected SHA tag continues to identify its original image and deployment does not depend on `latest`.

### User Story 3 - Set up public package access (Priority: P2)

A repository maintainer can complete any one-time GHCR package visibility setup and understand the required access configuration before relying on anonymous pulls.

**Why this priority**: Publication alone does not guarantee that deployment systems or users can pull the image publicly.

**Independent Test**: Follow the repository documentation's package setup instructions in GitHub and verify the package page indicates public visibility and anonymous image pulls succeed.

**Acceptance Scenarios**:

1. **Given** the package has not yet been made public, **When** a maintainer follows the documented one-time setup, **Then** the package is public and anonymous pulls work.
2. **Given** the setup is complete, **When** the maintainer reviews the instructions, **Then** they can distinguish the one-time visibility action from recurring automated publishing.

### Edge Cases

- A Docker build failure on a `main` push must be visible as a failed workflow and must not publish tags for an image that was not successfully built.
- A registry push failure or missing package-write permission must produce a failed workflow run rather than a successful publication result.
- A pull request from a fork must be able to perform build validation without a package write credential or permission.
- A failed `main` build must not move the `latest` tag to an image that was not successfully built.
- A commit with a full SHA identical to a prior run must resolve to the same source revision tag; publication must not imply that deployments should track `latest`.
- A private-by-default package must be identified in the setup documentation as requiring a one-time visibility change before anonymous pulls can work.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The repository MUST build its container image from the existing Dockerfile when a pull request targeting `main` is opened or updated.
- **FR-002**: A pull request image build MUST validate buildability without publishing any image or requesting package-write access.
- **FR-003**: When a commit is pushed to `main`, the repository MUST build the image and publish it to the repository's GHCR package only after the build succeeds.
- **FR-004**: A successful main-branch publication MUST provide a tag containing the complete source commit SHA and the mutable `latest` tag.
- **FR-005**: Full source commit SHA tags MUST identify the image built from that exact commit and MUST be treated as immutable by convention; consumers MUST be directed to deploy a selected SHA tag deliberately rather than track `latest`.
- **FR-006**: The publisher MUST use the workflow's built-in `GITHUB_TOKEN` and grant only the source-read and package-publish permissions required for its job. It MUST NOT require long-lived registry credentials.
- **FR-007**: Third-party actions used by the image workflow MUST be pinned to verified full commit SHAs and include readable version comments.
- **FR-008**: The image workflow MUST use safe pull request and main-branch triggers, and pull request execution MUST never publish or gain package-write permission.
- **FR-009**: The existing quality workflow and its checks MUST remain intact and continue to run for their existing pull request and main-branch events.
- **FR-010**: Repository documentation MUST state the GHCR package name or derivation, explain how to perform the one-time public visibility setup, and clarify that deployments select a full source SHA tag rather than `latest`.
- **FR-011**: Failed image builds or publication attempts MUST be reported as failed workflow runs and MUST NOT be reported as successful publication.

### Key Entities *(include if data involved)*

- **Source revision image**: The container image built from a specific repository commit, identified by its complete source commit SHA.
- **Convenience image tag**: The mutable `latest` reference updated by successful main-branch publication for convenient manual pulls.
- **GHCR package**: The repository-associated container package, whose visibility determines whether clients can pull images anonymously.
- **Workflow run**: A validation or publication attempt associated with a pull request or a main-branch commit and a visible success/failure result.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every pull request targeting `main` receives a visible container build result, and a successful pull request run creates zero published image tags.
- **SC-002**: Every successful `main` publication exposes both `latest` and a tag equal to the full source commit SHA for that run.
- **SC-003**: A user can anonymously pull a published full-SHA-tagged image after the one-time package visibility setup is complete.
- **SC-004**: A deliberately failing Docker build results in a failed workflow, publishes no image tags for that run, and does not report publication success.
- **SC-005**: The image workflow uses no long-lived registry credential and requests no permission beyond source read and package publication, with package-write permission absent from pull request validation.
- **SC-006**: The existing quality workflow definition and its lint, test, and package checks remain present and unchanged.
- **SC-007**: Repository documentation identifies the one-time action needed to make the GHCR package public and tells deployment maintainers to use a selected full-SHA tag.

## Assumptions

- The container image name is derived from this repository's GitHub owner and repository name, normalized as required by GHCR.
- The workflow runs for pull requests targeting `main` and for pushes to `main`; other refs are outside this publishing scope.
- GitHub Actions' built-in `GITHUB_TOKEN` can publish packages when granted package-write permission and the package/repository access relationship is configured appropriately.
- GHCR package visibility may require a one-time maintainer action after the package is first created; the repository will document that action.
- Package retention, signing, provenance attestations, multi-platform publishing, release tags, and deployment-manifest changes are outside this feature's scope.
