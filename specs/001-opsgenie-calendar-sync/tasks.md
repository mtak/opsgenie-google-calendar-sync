---
description: "Dependency-ordered implementation tasks for Opsgenie Calendar Sync"
---

# Tasks: Opsgenie Calendar Sync

**Input**: Design documents from `specs/001-opsgenie-calendar-sync/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/cli.md`, `quickstart.md`

**Tests**: Automated tests are included because the approved plan and project constitution require them. Write each test task before its corresponding implementation task and confirm the new test fails for the expected reason before implementing the behavior.

**Organization**: Tasks are grouped by the three P1 user stories. All user stories depend on shared project setup and foundational configuration/Google access.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Tasks can run in parallel because they touch different files and have no unmet dependencies.
- **[Story]**: User story traceability labels appear only on user-story phase tasks.
- Every task includes a concrete repository path.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the Python package, public-safe local configuration example, and container entry point.

- [X] T001 [P] Create `pyproject.toml` with Python 3.12 package metadata, the planned Google OAuth/Calendar and iCalendar runtime dependencies, and pytest development dependency.
- [X] T002 [P] Create the installable package entry file `src/opsgenie_google_calendar_sync/__init__.py` and shared pytest fixtures file `tests/conftest.py`.
- [X] T003 [P] Add nonfunctional placeholder settings to `config.example.toml` and ignore local settings, OAuth client files, and token files in `.gitignore`.
- [X] T004 Create `Dockerfile` and `docker-compose.yml` for a one-shot sync container that receives `OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR` and mounts that private directory read-only.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Validate local configuration and provide a tested Google Calendar gateway before user-story synchronization work begins.

- [X] T005 [P] Add configuration tests in `tests/unit/test_config.py` for required TOML keys, defaults, missing files, invalid values, and sanitized errors.
- [X] T006 Implement TOML loading, default path resolution, `OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR` override, and validation in `src/opsgenie_google_calendar_sync/config.py`.
- [X] T007 [P] Add mocked Google Calendar gateway tests in `tests/unit/test_google_calendar.py` for authorization loading, pagination, create/update/delete calls, and permission-denied responses.
- [X] T008 Implement the OAuth credential loader and Google Calendar event gateway in `src/opsgenie_google_calendar_sync/google_calendar.py`, including refresh-token use, pagination, and clear propagation of permission failures.

**Checkpoint**: Shared configuration and Google access are testable. No source-driven calendar mutations should be enabled before the story-specific feed validation and ownership safeguards are complete.

---

## Phase 3: User Story 1 - Keep the family calendar current (Priority: P1) 🎯 MVP

**Goal**: Read upcoming Opsgenie shifts and add or update matching Google Calendar events without duplicates.

**Independent Test**: Use synthetic iCalendar fixtures and an authorized dedicated test calendar; verify that upcoming source events appear once and changed times/details update the matching event.

### Tests for User Story 1

- [X] T009 [P] [US1] Add synthetic iCalendar fixtures and parser tests for source event fields, UIDs, time zones, and daylight-saving transitions in `tests/fixtures/` and `tests/unit/test_opsgenie_ical.py`.
- [X] T010 [P] [US1] Add fake-gateway reconciliation tests for adding missing events, updating changed events, and repeated-run idempotence in `tests/unit/test_reconcile.py`.

### Implementation for User Story 1

- [X] T011 [US1] Implement iCalendar feed retrieval and source event normalization in `src/opsgenie_google_calendar_sync/opsgenie_ical.py`, preserving source times, time zones, and available details.
- [X] T012 [US1] Implement add/update reconciliation by source UID in `src/opsgenie_google_calendar_sync/reconcile.py`, mapping source event details to Google Calendar event fields.
- [X] T013 [US1] Add the repeatable `sync` command in `src/opsgenie_google_calendar_sync/cli.py` and report successful run status with added, updated, and removed counts.

**Checkpoint**: User Story 1 works against a dedicated test calendar. Do not use the family calendar until User Story 3's failure and ownership safeguards are complete.

---

## Phase 4: User Story 2 - Run unattended with one-time authorization (Priority: P1)

**Goal**: Authorize Google once in a browser and run the sync daily from host cron without recurring sign-in.

**Independent Test**: Complete authorization once, run 30 simulated daily invocations without another interactive sign-in, and verify revoked authorization produces a visible failure.

### Tests for User Story 2

- [X] T014 [P] [US2] Add CLI authorization tests in `tests/unit/test_authorize.py` for successful consent completion, refresh-token persistence, and revoked/failed authorization handling.
- [X] T015 [P] [US2] Add a repeated-run test in `tests/unit/test_cli.py` that simulates 30 scheduled sync invocations after one authorization and verifies no interactive sign-in is needed.

### Implementation for User Story 2

- [X] T016 [US2] Implement the `authorize` command in `src/opsgenie_google_calendar_sync/cli.py` using the desktop OAuth flow and save the refresh token only to the configured private token file.
- [X] T017 [US2] Document Google Cloud project/API setup, consent-screen Production setting, browser authorization, secure token transfer, and host cron invocation in `specs/001-opsgenie-calendar-sync/quickstart.md`.

**Checkpoint**: User Story 2 can authorize once and run the sync as a one-shot Docker Compose job from host cron.

---

## Phase 5: User Story 3 - Protect unrelated family events and private setup (Priority: P1)

**Goal**: Restrict writes to sync-managed events, fail without changes on invalid source snapshots, preserve past shifts, and keep private values out of tracked files and logs.

**Independent Test**: With marked and unrelated events in a dedicated test calendar, exercise valid and invalid feed snapshots; verify only marked future events change, past events remain, invalid input causes zero writes, and output contains no private values.

### Tests for User Story 3

- [X] T018 [P] [US3] Add failure-safety tests in `tests/unit/test_failure_safety.py` proving empty, malformed, missing-UID, and duplicate-UID source feeds cause zero destination writes.
- [X] T019 [P] [US3] Add ownership and deletion-boundary tests in `tests/unit/test_managed_events.py` for unmarked events, manually edited managed events, future removals, and past-event retention, including the empty-feed no-op rule.
- [X] T020 [P] [US3] Add output privacy tests in `tests/unit/test_cli_privacy.py` proving feed URLs, calendar IDs, OAuth tokens, and event details are not emitted.
- [X] T021 [P] [US3] Add opt-in real Calendar API integration tests in `tests/integration/test_google_calendar.py`, gated on a dedicated test calendar and covering authorized create/update/delete behavior without using the family calendar.

### Implementation for User Story 3

- [X] T022 [US3] Reject empty, incomplete, malformed, unsupported, missing-UID, or duplicate-UID source snapshots before reconciliation in `src/opsgenie_google_calendar_sync/opsgenie_ical.py` and `src/opsgenie_google_calendar_sync/reconcile.py`.
- [X] T023 [US3] Privately compare sanitized Opsgenie feed observations before and after an upcoming shift edit/removal; record only UID stability, removal representation, and feed-window behavior in `specs/001-opsgenie-calendar-sync/research.md`, never storing the real URL or event data. The user accepts absence as deletion for marked future events in a valid non-empty feed; empty feeds remain a no-op.
- [X] T024 [US3] Mark created Google events with a private application marker and source UID; list and modify only marked events, delete unmatched future marked events only after a valid non-empty feed, and retain past events in `src/opsgenie_google_calendar_sync/google_calendar.py` and `src/opsgenie_google_calendar_sync/reconcile.py`.
- [X] T025 [P] [US3] Sanitize run output, return nonzero status for failed or partial writes, and create private OAuth/config files with restrictive permissions in `src/opsgenie_google_calendar_sync/cli.py` and `src/opsgenie_google_calendar_sync/config.py`.
- [X] T026 [US3] Document the verified feed behavior, fail-closed behavior, and dedicated-test-calendar checks in `specs/001-opsgenie-calendar-sync/quickstart.md`.

**Checkpoint**: All three user stories meet their safety and acceptance criteria; the family calendar can be selected only after source behavior and the opt-in integration tests have been validated.

---

## Phase 6: Polish & Cross-Cutting Verification

**Purpose**: Verify the complete user flow, performance goal, and deployment configuration after implementation.

- [X] T027 Run the automated suite, opt-in integration tests against a dedicated test calendar, and `docker compose config`; measure a representative few-hundred-event sync against the plan's one-minute goal and record results in `specs/001-opsgenie-calendar-sync/quickstart.md`.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001, T002, and T003 can run in parallel; T004 depends on the package/dependency and private-config conventions from T001 and T003.
- **Foundational (Phase 2)**: Starts after setup. T005 and T007 can run in parallel; T006 follows T005; T008 follows T006 and T007.
- **User Stories (Phases 3–5)**: All depend on the foundational phase and are ordered by their dependencies below.
- **Polish (Phase 6)**: T027 depends on every implementation, feed-validation, integration-test, and documentation task.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Phase 2; it provides the working source-to-calendar sync command.
- **User Story 2 (P1)**: Depends on User Story 1 because authorization and cron must invoke the working sync command.
- **User Story 3 (P1)**: Depends on User Story 1's reconciliation path and User Story 2's CLI authorization/logging paths. Source-absence deletion specifically depends on successful T023 feed validation.

### Within Each User Story

- Write and run each listed test before implementing its behavior; confirm the new test fails for the intended reason.
- Implement feed normalization before source-to-Google reconciliation.
- Record sanitized Opsgenie UID, removal, and feed-window observations; use the user's non-empty-feed deletion policy with private-marker ownership and UID-rotation matching.
- Implement future deletion and privacy protections only after their tests exist.
- Complete each phase checkpoint before proceeding to the next story.

### Parallel Opportunities

- Setup tasks T001, T002, and T003 touch separate files and can start together.
- Foundational tests T005 and T007 cover separate modules and can be written together.
- User Story 1 test tasks T009 and T010 cover separate files and can be written together.
- User Story 2 test tasks T014 and T015 cover separate files and can be written together.
- User Story 3 test tasks T018–T021 cover separate files and can be written together.
- After T018–T023 prerequisites are complete, T024 deletion work and T025 privacy-output work touch different files and may proceed in parallel.

---

## Parallel Examples

### User Story 1

```text
Task T009: Create iCalendar parser fixtures and tests in tests/fixtures/ and tests/unit/test_opsgenie_ical.py
Task T010: Create reconciliation tests in tests/unit/test_reconcile.py
```

### User Story 2

```text
Task T014: Create authorization-flow tests in tests/unit/test_authorize.py
Task T015: Create 30-invocation test in tests/unit/test_cli.py
```

### User Story 3

```text
Task T018: Create source-failure safety tests in tests/unit/test_failure_safety.py
Task T019: Create managed-event boundary tests in tests/unit/test_managed_events.py
Task T020: Create privacy tests in tests/unit/test_cli_privacy.py
Task T021: Create opt-in Calendar API tests in tests/integration/test_google_calendar.py
```

## Implementation Strategy

### MVP First

1. Complete Setup and Foundational phases.
2. Complete User Story 1 and validate add/update/idempotence using a dedicated test calendar.
3. Complete User Story 2 for the one-time authorization and daily host cron flow.
4. Complete User Story 3 before directing any run at the real family calendar; source-absence deletion is limited to app-marked future events after a valid non-empty feed.

User Story 1 is the smallest demonstrable sync increment, but the full personal-use MVP requires all three P1 stories: authorization and scheduling for unattended use, plus ownership and failure safeguards for the family calendar.

### Incremental Delivery

1. Build configuration and the Google Calendar gateway.
2. Add feed parsing and add/update reconciliation; validate on a dedicated test calendar.
3. Add browser authorization and cron deployment documentation.
4. Add fail-closed source validation and privacy protections.
5. Apply the recorded non-empty-feed deletion policy and validate ownership boundaries on a dedicated calendar before using the family calendar.
6. Add managed-event deletion boundaries and run integration/performance checks.

## Notes

- Every task uses the required checkbox, sequential task ID, optional parallel marker, story label in story phases, and at least one concrete file path.
- [P] tasks target separate files with no unmet dependencies.
- Private configuration examples must use nonfunctional placeholders; never capture the live Opsgenie feed in Git.
- The plan's one-minute performance goal is validated by T027 on a representative event set.
- This task list does not authorize coding by itself; implementation work remains subject to the project's review gates.

## Phase 7: Convergence

**Purpose**: Close test-coverage gaps found by comparing the current implementation with the approved requirements and plan. The remaining live feed and dedicated-calendar work is already tracked by T019, T023, T024, and T027.

- [X] T028 [P] Add parser tests for RRULE/RDATE/EXRULE/EXDATE/RECURRENCE-ID recurrence forms, cancellation, and incomplete VEVENT fields, proving these unsupported or incomplete source snapshots fail validation before destination access in `tests/unit/test_opsgenie_ical.py` (FR-009, partial).
- [X] T029 [P] Link one successful mocked authorization and persisted refresh token to 30 scheduled sync invocations without an interactive flow in `tests/unit/test_authorize.py` and `tests/unit/test_cli.py` (SC-006, partial).
- [X] T030 [P] Assert the Google Calendar gateway queries only events with this application's private marker and verify unmarked events never reach a mutation path in `tests/unit/test_google_calendar.py` and `tests/unit/test_managed_events.py` (FR-005, partial).

## Phase 8: Convergence

**Purpose**: Add regression coverage for two implemented fail-safe behaviors that were not explicitly verified by the existing test suite.

- [X] T031 [P] Add a test proving duplicate marked Google events with the same source UID cause reconciliation to fail before any writes in `tests/unit/test_managed_events.py` (FR-005, partial).
- [X] T032 [P] Add a test proving a later-page Calendar event-list failure causes reconciliation to fail before create, update, or delete operations in `tests/unit/test_google_calendar.py` and `tests/unit/test_reconcile.py` (FR-010, plan: reconciliation steps 4–6, partial).

## Phase 9: Convergence

**Purpose**: Close the remaining live ownership-boundary verification gap.

- [X] T033 Run reconciliation against a disposable dedicated Google Calendar containing an unmarked sentinel and managed events; verify add, update, deletion of an absent future managed event, preservation of the sentinel and past managed events, and the empty-feed no-op in `tests/integration/test_google_calendar.py` and record the result in `specs/001-opsgenie-calendar-sync/quickstart.md` (FR-005, FR-006, FR-009; US3 ownership-boundary verification).
