# Implementation Plan: Rename the Project

**Branch**: `002-rename-project` | **Date**: 2026-10-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/002-rename-project/spec.md`

## Summary

Rename the project's public and internal identity from `oncall-calendar-sync` to `opsgenie-google-calendar-sync`. Update Python distribution and import names, CLI and container entry points, configuration defaults and override variable, example and specification documentation, then rename the GitHub repository and the primary local checkout. Preserve all synchronization behavior. The user's current local installation migration and auxiliary worktree paths, branches, contents, and remotes are out of scope; Git pointers may be repaired to keep those worktrees connected.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: setuptools, pytest, Google API Python client, Google Auth OAuth library, icalendar; no dependency changes planned

**Storage**: TOML configuration and OAuth JSON files remain outside the repository; no storage schema changes

**Testing**: pytest unit and integration suites; package installation and CLI invocation checks

**Target Platform**: Python 3.12 on Docker and the local development host; repository rename managed through GitHub

**Project Type**: Python command-line application

**Performance Goals**: No performance change; preserve existing synchronization behavior

**Constraints**: Do not change reconciliation, event data, OAuth scopes, or the user's local installation; preserve auxiliary worktree paths, branches, contents, and remotes, repairing Git pointers only as needed; update the primary checkout path to `~/dev/opsgenie-google-calendar-sync`; repository owner remains `mtak`

**Scale/Scope**: One Python package, its CLI, Docker setup, config example, project documentation/specification references, one GitHub repository, and one primary local checkout

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Specification-driven development: PASS — approved feature specification exists and this plan is its design artifact.
- Approval before implementation: PASS — implementation and GitHub/local checkout changes wait for approval of this plan.
- Small, reviewable changes: PASS — implementation is divided into code/docs and repository-location increments.
- Automated verification: PASS — the existing automated suite and package/CLI checks are part of validation after code changes.
- Repository guidance: PASS — work remains within the approved rename scope; no synchronization architecture changes are planned.

## Project Structure

### Documentation (this feature)

```text
specs/002-rename-project/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── rename-surfaces.md
└── tasks.md                 # Created by $speckit-tasks
```

### Source Code (repository root)

```text
pyproject.toml
Dockerfile
docker-compose.yml
config.example.toml
src/opsgenie_google_calendar_sync/
├── __init__.py
├── cli.py
├── config.py
├── google_calendar.py
├── opsgenie_ical.py
└── reconcile.py
tests/
├── conftest.py
├── integration/
└── unit/
specs/
├── 001-opsgenie-calendar-sync/  # Existing specification and setup documentation updated to canonical names
└── 002-rename-project/
.specify/memory/constitution.md  # Project title updated
```

**Structure Decision**: Keep the existing single Python CLI layout. Rename the import package directory to `src/opsgenie_google_calendar_sync` and update its tests and all documentation references. Do not introduce new runtime components or dependencies.

## Implementation Phases

### Phase 1 — Rename code and repository documentation

1. Rename the Python package directory and all source/test imports to `opsgenie_google_calendar_sync`.
2. Set the distribution name and executable to `opsgenie-google-calendar-sync`; update the argparse program name and HTTP User-Agent product token.
3. Set the default config directory to `~/.config/opsgenie-google-calendar-sync` and rename project-specific override and integration-test environment variables to the `OPSGENIE_GOOGLE_CALENDAR_SYNC_` prefix in Python, Docker, Compose, tests, examples, and docs. The former local installation is explicitly outside this work.
4. Update the Docker entry point, environment variable, and documented Compose/cron commands to the canonical names.
5. Update `config.example.toml`, the existing feature docs under `specs/001-opsgenie-calendar-sync/`, this project's constitution title, and all other tracked active documentation references. Keep former-name references only where needed to describe the rename in this feature's specification.
6. Preserve the private Google Calendar extended-property name `oncallCalendarSync` and its `SYNC_MARKER` value format so existing managed events remain recognized; no synchronization metadata changes.
7. Run the unit and integration suites with the live-calendar integration flag unset, install the package in an isolated environment, and confirm the canonical command starts and reports help/usage correctly.

**Completion gate**: tests pass; installation and CLI use the canonical identity; a case-insensitive repository scan finds no stale active-name references outside the rename explanation or the stable private calendar-event marker; synchronization behavior is unchanged.

### Phase 2 — Rename GitHub repository and primary local checkout

1. Rename `mtak/oncall-calendar-sync` to `mtak/opsgenie-google-calendar-sync` in GitHub repository settings after Phase 1 is reviewed and ready.
2. Enable Git worktree-specific configuration in the primary checkout and move its existing `core.bare=false` value from the shared config into the primary worktree config as required by Git. Keep the shared `remote.origin.url` unchanged; add a primary-worktree-only `url.<canonical>.insteadOf` rule so the primary checkout resolves `origin` to `https://github.com/mtak/opsgenie-google-calendar-sync.git` while auxiliary worktrees continue to resolve the shared old URL.
3. Rename `~/dev/oncall-calendar-sync` to `~/dev/opsgenie-google-calendar-sync` while preserving all contents, including untracked files. Do not move or change auxiliary worktree paths, branches, contents, or remotes, or alter the user's external local installation.
4. Run `git worktree repair` from the moved primary checkout to restore linked-worktree connections, without changing their paths, branches, contents, or remotes.
5. Confirm the primary checkout reports the new root path and remote, can fetch from the renamed repository, and linked worktrees remain connected.

**Completion gate**: GitHub shows the canonical repository name; the primary local directory and `origin` use the new name; auxiliary worktree pointers are repaired if needed while their paths, branches, contents, and remotes remain unchanged; external installation is untouched.

## Constitution Check (Post-Design)

- Specification-driven development: PASS — design artifacts trace to FR-001–FR-007 and the clarified primary-checkout scope.
- Approval before implementation: PASS — no implementation or external repository changes occur until this plan is approved.
- Small, reviewable changes: PASS — code/docs and external repository/location updates have separate completion gates.
- Automated verification: PASS — automated tests run after code changes; repository identity is checked independently.
- Repository guidance: PASS — no new architecture, dependencies, or synchronization behavior are introduced.

## Complexity Tracking

No constitution violations or added architectural complexity.
