---
description: "Dependency-ordered implementation tasks for the project rename"
---

# Tasks: Rename the Project

**Input**: Design documents from `specs/002-rename-project/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: No new tests are requested. Existing tests must be updated for renamed imports/settings and run after code changes, as required by the project constitution.

**Organization**: Tasks are grouped by user story. User Story 2 follows User Story 1 because the plan requires code and documentation identity to be ready before renaming the GitHub repository and primary checkout.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel with other marked tasks after dependencies are complete.
- **[Story]**: Maps a task to the matching user story in `spec.md`.
- Each task includes the files or repository path it changes or verifies.

## Path Conventions

- Python CLI source: `src/opsgenie_google_calendar_sync/`
- Tests: `tests/unit/` and `tests/integration/`
- Project docs: `specs/001-opsgenie-calendar-sync/`
- Rename feature artifacts: `specs/002-rename-project/`

## Phase 1: Setup

**Purpose**: The existing Python 3.12 project and test layout are already initialized. No setup changes or dependency additions are required.

## Phase 2: Foundational

**Purpose**: No shared infrastructure blocks either story. Begin User Story 1 after the implementation plan is approved; User Story 2 depends on completion of User Story 1.

## Phase 3: User Story 1 - Use the renamed project (Priority: P1) 🎯 MVP

**Goal**: New installations, operators, and contributors encounter `opsgenie-google-calendar-sync` across package, command, config defaults, container, and current setup documentation, while synchronization behavior and event markers remain unchanged.

**Independent Test**: Install the project in an isolated Python 3.12 environment, confirm the canonical executable and default config path, run the existing suite with live Calendar integration disabled, and inspect current setup docs for canonical names.

### Implementation for User Story 1

- [X] T001 [US1] Rename the package directory `src/oncall_calendar_sync/` to `src/opsgenie_google_calendar_sync/`, preserving all six module files and their contents.
- [X] T002 [P] [US1] Update the distribution name and console entry point in `pyproject.toml`, the displayed program name in `src/opsgenie_google_calendar_sync/cli.py`, and the HTTP User-Agent product token in `src/opsgenie_google_calendar_sync/opsgenie_ical.py`; retain the existing synchronization behavior and private event marker.
- [X] T003 [P] [US1] Set the default configuration directory and `OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR` override in `src/opsgenie_google_calendar_sync/config.py`, and update the package import and corresponding environment-variable expectation in `tests/unit/test_config.py`.
- [X] T004 [P] [US1] Change package imports and mock target paths to `opsgenie_google_calendar_sync` in `tests/unit/test_authorize.py`, `tests/unit/test_cli.py`, `tests/unit/test_cli_privacy.py`, `tests/unit/test_failure_safety.py`, `tests/unit/test_google_calendar.py`, `tests/unit/test_managed_events.py`, `tests/unit/test_opsgenie_ical.py`, `tests/unit/test_reconcile.py`, and `tests/integration/test_google_calendar.py`; rename integration-test environment variables to the `OPSGENIE_GOOGLE_CALENDAR_SYNC_` prefix.
- [X] T005 [P] [US1] Set the canonical executable and `OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR` environment name in `Dockerfile` and `docker-compose.yml`, keeping the container's private config mount read-only.
- [X] T006 [P] [US1] Update the example config and operator setup contract in `config.example.toml`, `specs/001-opsgenie-calendar-sync/quickstart.md`, and `specs/001-opsgenie-calendar-sync/contracts/cli.md` to use the canonical config path, command, environment variable, and repository checkout name; do not add current-install migration instructions.
- [X] T007 [P] [US1] Replace stale active project, package, config-path, and environment-variable names in `specs/001-opsgenie-calendar-sync/plan.md`, `specs/001-opsgenie-calendar-sync/research.md`, `specs/001-opsgenie-calendar-sync/data-model.md`, `specs/001-opsgenie-calendar-sync/tasks.md`, and update the project title in `.specify/memory/constitution.md`.
- [X] T008 [US1] Run the package-install, canonical CLI help, default-config-path, Docker Compose configuration, and existing pytest checks in `specs/002-rename-project/quickstart.md`; leave `OPSGENIE_GOOGLE_CALENDAR_SYNC_INTEGRATION` unset so tests do not use a live calendar.

**Checkpoint**: User Story 1 is independently usable when the canonical package and command install successfully, the new configuration default resolves correctly, setup documentation uses the new name, and synchronization metadata remains unchanged.

## Phase 4: User Story 2 - Find and check out the renamed repository (Priority: P2)

**Goal**: Rename the existing GitHub repository in place and update only the primary local checkout to the canonical name while preserving its files and the connections of auxiliary worktrees.

**Independent Test**: Confirm the GitHub repository is `mtak/opsgenie-google-calendar-sync`, the primary directory and `origin` use the canonical name, the remote is reachable, and auxiliary worktree paths, branches, contents, and remotes are unchanged after pointer repair.

### Repository and checkout rename

- [X] T009 [US2] Rename the existing GitHub repository from `mtak/oncall-calendar-sync` to `mtak/opsgenie-google-calendar-sync` in its repository settings, after User Story 1 is complete and the plan is approved.
- [X] T010 [US2] In the primary checkout at `~/dev/oncall-calendar-sync`, move `core.bare=false` from the shared config into worktree config, enable `extensions.worktreeConfig`, then add a worktree-specific `url.<canonical>.insteadOf` rule mapping the old URL to `https://github.com/mtak/opsgenie-google-calendar-sync.git`; leave the shared remote URL unchanged for auxiliary worktrees.
- [X] T011 [US2] Rename `~/dev/oncall-calendar-sync` to `~/dev/opsgenie-google-calendar-sync` from `~/dev`, preserving tracked and untracked contents.
- [X] T012 [US2] Run `git worktree repair` from `~/dev/opsgenie-google-calendar-sync` only to restore linked-worktree Git pointers; leave auxiliary worktree paths, branches, contents, and remotes unchanged.
- [X] T013 [US2] Verify the primary checkout root and remote; clone `https://github.com/mtak/opsgenie-google-calendar-sync.git` into a temporary directory named `opsgenie-google-calendar-sync` and confirm its root and `origin`; verify the old Git URL with `git ls-remote https://github.com/mtak/oncall-calendar-sync.git HEAD` and the old repository lookup with authenticated `gh repo view mtak/oncall-calendar-sync --json nameWithOwner,url`; remove the temporary clone and confirm auxiliary worktrees remain at their original paths with the original shared remote URL.

**Checkpoint**: User Story 2 is complete when the GitHub URL and primary checkout path are canonical, the primary remote fetches successfully, and linked worktrees remain connected without changes to their paths, branches, contents, or remotes.

## Phase 5: Polish & Cross-Cutting Verification

**Purpose**: Confirm the rename is consistent and existing synchronization behavior is preserved.

- [X] T014 Audit tracked source, tests, configuration, and current documentation from the repository root for stale active project identity using `rg`; permit former-name references only in `specs/002-rename-project/` where needed to describe the rename and preserve the private event property in `src/opsgenie_google_calendar_sync/google_calendar.py` and `SYNC_MARKER` value in `src/opsgenie_google_calendar_sync/reconcile.py`.

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No changes required; the project and dependencies already exist.
- **Foundational (Phase 2)**: No implementation tasks; approved design artifacts provide the shared requirements.
- **User Story 1 (Phase 3)**: Begins after the implementation plan is approved. T001 must complete before T002–T007; T002–T007 can then run in parallel because they change separate files. T008 follows T002–T007.
- **User Story 2 (Phase 4)**: Depends on completion and review of User Story 1. T009 → T010 → T011 → T012 → T013 must run in order.
- **Polish (Phase 5)**: T014 runs after User Story 2 and audits the final source, documentation, and repository identity.

### User Story Dependencies

- **User Story 1 (P1)**: No dependency on User Story 2; it delivers the canonical package, command, configuration defaults, container, and setup documentation.
- **User Story 2 (P2)**: Depends on User Story 1 so repository and checkout identity change after code and documentation are ready.

### Parallel Opportunities

- After T001, tasks T003, T004, T005, T006, and T007 edit separate files and can proceed in parallel; T002 also follows T001 and can run in parallel with them.
- No User Story 2 tasks are parallel because each repository/checkout action depends on the preceding state change.
- T014 follows T013 so the final identity audit runs after all repository and checkout changes are complete.

## Parallel Example: User Story 1

```text
After T001 is complete, run these independent file groups in parallel:
Task: T002 update pyproject.toml and the renamed CLI/User-Agent source files
Task: T003 update src/opsgenie_google_calendar_sync/config.py and tests/unit/test_config.py
Task: T004 update the remaining tests/unit/ and tests/integration/ imports and test environment names
Task: T005 update Dockerfile and docker-compose.yml
Task: T006 update config.example.toml and the operator-facing quickstart/CLI contract
Task: T007 update the remaining specs/001 documentation and constitution title
```

## Implementation Strategy

### MVP First (User Story 1)

1. Complete T001 to establish the canonical Python import directory.
2. Complete T002–T007, in parallel where shown.
3. Complete T008 to validate installation, CLI/config names, Compose, and existing tests.
4. Stop for review before the external GitHub and primary checkout changes in User Story 2.

### Incremental Delivery

1. Deliver User Story 1 as the code/documentation rename MVP.
2. After review, complete User Story 2 by renaming the GitHub repository and primary local checkout.
3. Complete final verification and preserve auxiliary worktree connections.

## Notes

- `[P]` marks tasks that can run in parallel after listed dependencies are complete.
- `[US1]` and `[US2]` map tasks to the corresponding stories in `spec.md`.
- No new tests are added; existing tests are updated for renamed module and environment identifiers and run for required verification.
- The external GitHub rename and primary checkout move occur only after approval of `plan.md`.
