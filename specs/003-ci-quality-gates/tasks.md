---
description: "Dependency-ordered implementation tasks for CI Quality Gates"
---

# Tasks: CI Quality Gates

**Input**: Design documents from `specs/003-ci-quality-gates/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/ci.md`, `quickstart.md`

**Tests**: The existing pytest suite is run as one CI job. No new application behavior or test module is required; local and pull request validation is specified below.

**Organization**: Tasks are grouped by the two P1 user stories. The setup task establishes shared lint configuration before the CI story uses it.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Tasks can run in parallel because they touch different files and have no unmet dependencies.
- **[Story]**: User story traceability labels appear only on user-story phase tasks.
- Every task includes a concrete repository path or an explicit repository settings location.

## Phase 1: Setup (Shared Configuration)

**Purpose**: Add the modest lint baseline and make the same command available to contributors and CI.

- [X] T001 Add Ruff to the `dev` optional dependency and configure the Python 3.12 target with the modest `E4`, `E7`, `E9`, and `F` rule families in `pyproject.toml`.

---

## Phase 2: User Story 1 - Review Changes with Automated Quality Checks (Priority: P1) 🎯 MVP

**Goal**: Report separate lint, test, and package-build outcomes for pull requests and `main`, and require each result before merging.

**Independent Test**: Run the three commands locally, then confirm each has its own status on a pull request and that GitHub blocks merging if any required status is failed or incomplete.

### Implementation for User Story 1

- [X] T002 Add `.github/workflows/quality.yml` for pull requests targeting `main` and pushes to `main`, with separate stable `lint`, `tests`, and `build` jobs, Python 3.12, read-only `contents` permission, no secrets, and third-party actions pinned to verified full commit SHAs.
- [X] T003 Configure repository branch protection for `main` to require the `lint`, `tests`, and `build` statuses; document the active rule in `specs/003-ci-quality-gates/quickstart.md`.
- [X] T004 Validate the Ruff, pytest, and wheel/source distribution build commands locally and confirm the workflow's job commands match `specs/003-ci-quality-gates/contracts/ci.md` and `specs/003-ci-quality-gates/quickstart.md`.

**Checkpoint**: All three checks produce independent results, and the `main` merge rule requires each check to pass.

---

## Phase 3: User Story 2 - Follow the Documented Command (Priority: P1)

**Goal**: Make every README invocation match the executable installed by the project.

**Independent Test**: Compare `[project.scripts]` in `pyproject.toml` with all command examples and the CLI reference in `README.md`; install the project and invoke the documented command's help output.

### Implementation for User Story 2

- [X] T005 [P] Replace stale `oncall-calendar-sync` invocations with `opsgenie-google-calendar-sync` in `README.md` and check the installation, authorization, sync, and CLI examples for consistency with `pyproject.toml`.

**Checkpoint**: Every documented command uses the executable declared in package metadata.

---

## Phase 4: Polish & Cross-Cutting Verification

**Purpose**: Verify the changes as a whole and keep feature task status aligned with implementation.

- [X] T006 Run `ruff check .`, `pytest`, and `python -m build`; confirm the README command references match `pyproject.toml` and review the final workflow with the GitHub Actions hardening checklist.
- [X] T007 Update `specs/003-ci-quality-gates/quickstart.md` with actual local validation results and any repository-side merge-rule status that cannot be enabled until workflow checks exist on GitHub.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 is required before the lint job can use a committed Ruff configuration and development dependency.
- **User Story 1 (Phase 2)**: T002 depends on T001. T003 depends on T002 having produced the required check names; GitHub must have observed the statuses before they can be selected in some ruleset flows. T004 depends on T001 and T002.
- **User Story 2 (Phase 3)**: T005 is independent of the CI workflow and can proceed after Setup.
- **Polish (Phase 4)**: T006 depends on T001, T002, and T005. T007 depends on local verification and the status of repository settings.

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Setup; establishes the CI and merge gate.
- **User Story 2 (P1)**: Independent after Setup; fixes the operator-facing executable name.

### Parallel Opportunities

- T005 can be implemented alongside T002 after T001 because it edits a different file.
- T004 can follow workflow creation while T005 is underway.

## Implementation Strategy

### MVP First

1. Complete T001 and T002 to establish the three checks.
2. Complete T004 to verify the local check commands and their CI alignment.
3. Complete T003 once the GitHub check statuses are available, so the merge gate matches real status names.

### Incremental Delivery

1. Add the shared Ruff development configuration.
2. Add and validate the three CI jobs.
3. Correct the README command independently.
4. Activate required status checks after the workflow reports them, then run final validation.

## Notes

- CI jobs use stable names because repository merge protection references status names.
- Use `pull_request`, not a privileged pull-request trigger; the workflow runs untrusted contributor code with read-only permissions and no secrets.
- Pin action references to verified full commit SHAs and include readable version comments.
- The repository ruleset is GitHub-side configuration and cannot be activated from tracked YAML alone.
- Keep the source diff limited to workflow, `pyproject.toml`, and `README.md`; feature documentation records validation and setup.

## Phase 5: Convergence

**Purpose**: Activate and verify the merge gate in the GitHub repository after the workflow is published.

- [X] T008 Publish the quality workflow on a pull request targeting `main`, configure branch protection to require `lint`, `tests`, and `build`, and record the active rule in `specs/003-ci-quality-gates/quickstart.md` (FR-004).
