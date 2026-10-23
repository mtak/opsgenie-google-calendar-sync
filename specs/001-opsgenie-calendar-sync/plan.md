# Implementation Plan: Opsgenie Calendar Sync

**Branch**: `001-opsgenie-calendar-sync` | **Date**: 2026-10-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/001-opsgenie-calendar-sync/spec.md`

## Summary

Build a small Python command-line sync that reads one Opsgenie iCalendar feed and reconciles upcoming shifts into one selected family Google Calendar. Use Google’s installed desktop OAuth flow for one-time browser authorization, with a locally protected refresh-token file for unattended runs. Store source identity on each sync-created Google event, so the job can find and manage only its own events without a database. Run the job as a one-shot Docker Compose task from the always-on machine’s cron. Fetch and fully validate the feed before changing Google Calendar; retain past shifts and fail closed on empty, invalid, or ambiguous input.

## Technical Context

**Language/Version**: Python 3.12 (conservative baseline; lock supported versions when implementing)

**Primary Dependencies**: Google API Python client, Google Auth OAuth library, iCalendar parser; versions to select at implementation

**Storage**: Google Calendar event metadata for sync identity; local private configuration and OAuth token file mounted into the container; no database

**Testing**: pytest unit tests with sanitized iCalendar fixtures and mocked Google Calendar calls; manual end-to-end check against a separate test calendar

**Target Platform**: Linux host with Docker Compose and cron; initial OAuth authorization runs on a machine with a browser

**Project Type**: Small command-line application / scheduled batch job

**Performance Goals**: Complete one daily sync of a single on-call feed and one family calendar in under one minute under normal service conditions

**Constraints**: Public repository; no real feed URL, calendar ID, OAuth token, or account-specific data in tracked files or logs. OAuth refresh token must be persisted outside the repository. No destination mutations before a complete successful source read and validation. Google authorization can be revoked and must fail visibly.

**Scale/Scope**: One personal deployment, one Opsgenie feed, one destination calendar, and at most a few hundred upcoming events per run.

## Constitution Check

- **I. Specification-Driven Development**: PASS. This plan follows the approved feature specification; the next stages are task generation and implementation after plan approval.
- **II. Approval Before Planning and Implementation**: PASS. The user directed the work to proceed after reviewing the draft specification. Coding remains gated on approval of this plan.
- **III. Small, Reviewable Changes**: PASS. Implementation is planned in independently reviewable increments: configuration and parsing, authorization and Google access, reconciliation, then container and scheduling documentation.
- **IV. Automated Verification**: PASS. The plan includes automated tests for parsing, reconciliation, failure safety, and API behavior; tests will run after code changes.
- **V. Repository Guidance Is Authoritative**: PASS. The feature specification remains the behavior source of truth; this plan resolves technical choices without changing its one-way scope.

**Gate result**: PASS. No constitution violations identified.

## Project Structure

### Documentation (this feature)

```text
specs/001-opsgenie-calendar-sync/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli.md
└── tasks.md                 # Generated in the next Spec Kit stage
```

### Source Code (repository root)

```text
src/oncall_calendar_sync/
├── __init__.py
├── cli.py                   # authorize and sync commands
├── config.py                # private runtime configuration validation
├── opsgenie_ical.py         # fetch and parse source feed
├── google_calendar.py       # OAuth client and Calendar operations
└── reconcile.py             # compare desired source events with managed events

tests/
├── fixtures/                # synthetic, non-private iCalendar files
├── unit/
│   ├── test_opsgenie_ical.py
│   ├── test_config.py
│   └── test_reconcile.py
└── integration/
    └── test_google_calendar.py  # opt-in, requires a dedicated test calendar

Dockerfile
docker-compose.yml
config.example.toml
.gitignore                  # excludes private local configuration and token files
```

**Structure Decision**: Use one small Python package and a CLI. Keep source-feed parsing, Google Calendar access, and reconciliation separate so the highest-risk rules can be tested without live credentials. Do not add a database, web server, or self-scheduling process. Keep operator config outside the repository at `~/.config/oncall-calendar-sync/`. Use a TOML settings file plus the OAuth client and token JSON files in that directory; mount the directory read-only into the sync container. Use Docker Compose for repeatable execution and host cron for the daily trigger.

## Phase 0: Research Findings

See [research.md](research.md). Decisions include a desktop OAuth flow for one personal user, Google event private extended properties for source identity, one-shot Compose execution from cron, and fail-closed reconciliation. A sanitized feed check remains a prerequisite for safely enabling source-driven deletion because Opsgenie does not document UID stability or cancellation encoding.

## Phase 1: Design

### Data Model

See [data-model.md](data-model.md). The design has four records: source shift, sync-managed Google event, private runtime configuration, and sync run result. The sync marker and source UID live in private metadata on the Google event, avoiding a separate database.

### CLI Contract

See [contracts/cli.md](contracts/cli.md). The user-facing contract is limited to one-time `authorize` and repeatable `sync` commands. Both read `~/.config/oncall-calendar-sync/config.toml` by default; an alternate config directory may be selected for Docker and headless-host setup. Scheduled runs report only result and change counts; they do not print event details or private configuration.

### Operational Setup

See [quickstart.md](quickstart.md). The setup requires creating a Google Cloud project, enabling Calendar API, configuring the OAuth consent screen, creating a Desktop app OAuth client, authorizing once in a browser, and storing the resulting token outside the repository. Runtime files live in `~/.config/oncall-calendar-sync/`: `config.toml`, `oauth-client.json`, and `token.json`. For a personal app with fewer than 100 users, Google says verification is not required, but the app remains unverified and shows a warning. The consent screen must not remain in Testing, because test authorizations expire after seven days.

The Google OAuth scope depends on calendar ownership. Use the narrowest supported events scope that lets the authorized account edit the selected calendar: `calendar.events.owned` if that account owns it; otherwise evaluate `calendar.events`, which covers event access across calendars that account can access. Verify the calendar owner and editor access before choosing the scope. This permission breadth is the main security tradeoff to review before implementation.

### Reconciliation Flow

1. Load and validate private configuration and authorization paths without printing their values.
2. Fetch the complete iCalendar response. Reject network errors, malformed calendars, empty feeds, duplicate or missing UIDs, and unsupported event shapes before any Google writes.
3. Convert upcoming source events to a normalized desired event set, preserving source start/end times and timezone semantics.
4. List only Google events marked with this application's private sync property; handle pagination and limit reconciliation to the active upcoming source window.
5. Match events by source UID. Insert missing events, update changed fields, and remove future managed events absent from a successfully validated source feed. Preserve past managed events and all unmarked events.
6. Record per-operation failures truthfully. A failed or partial destination write returns a nonzero status; a subsequent run reconciles from current source state and existing managed events.
7. Emit a sanitized summary with status and added/updated/removed counts. Never log event titles, source URLs, calendar IDs, OAuth tokens, or response bodies containing private values.

### Test Strategy

- Unit tests use synthetic iCalendar fixtures for normal shifts, timezone offsets, daylight-saving transitions, missing/duplicate UIDs, empty feeds, malformed content, and source updates/removals.
- Reconciliation tests use a fake Calendar gateway to verify idempotence, sync ownership, past-event retention, deletion boundaries, and no writes after an invalid source read.
- OAuth and Calendar client tests mock token refresh, revoked authorization, permission failures, API pagination, and partial write errors.
- Manual integration uses a dedicated test calendar, never the family calendar for destructive scenarios. Confirm one-time authorization, repeated sync, source edit, future removal, past retention, and unrelated-event preservation.
- Opsgenie feed behavior must be checked before implementing source-absence deletion. Compare observations around a shift edit/removal and record only UID stability, removal representation, and feed-window behavior in `research.md`; do not save the real feed URL or event data in Git. If a complete deletion signal cannot be established, leave source-absence deletion disabled.
- Run opt-in Calendar API integration tests only against a dedicated test calendar.
- Measure a representative few-hundred-event sync against the one-minute performance goal and record the result in `quickstart.md`.

## Constitution Check (Post-Design)

- **I. Specification-Driven Development**: PASS. Design implements only the approved one-way sync requirements.
- **II. Approval Before Planning and Implementation**: PASS. User approval of this plan is required before coding.
- **III. Small, Reviewable Changes**: PASS. The package boundaries and test groups support incremental implementation.
- **IV. Automated Verification**: PASS. Each code increment has automated unit or integration verification planned.
- **V. Repository Guidance Is Authoritative**: PASS. No specification requirements were silently dropped; unresolved feed semantics are recorded as a pre-implementation validation item.

**Post-design gate result**: PASS, with the Opsgenie feed validation noted above as an implementation prerequisite.

## Complexity Tracking

No constitution violations. This is a single local batch application with one external read source, one authorized write destination, and no server or database. The required Cloud Console setup and broader OAuth scope (if the calendar is not owned by the authorized account) are documented tradeoffs, not reasons to add infrastructure.
