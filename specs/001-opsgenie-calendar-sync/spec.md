# Feature Specification: Opsgenie Calendar Sync

**Feature Branch**: `001-opsgenie-calendar-sync`

**Created**: 2026-10-23

**Status**: Draft

**Input**: User description: A daily one-way sync from an Opsgenie on-call iCalendar feed into a family's shared Google Calendar, running on an always-on machine. The repository is public and must contain no private configuration or credentials.

## Clarifications

### Session 2026-10-23

- Q: If any upcoming Opsgenie event in the feed has no stable identifier or cannot be parsed, should that run stop before changing Google Calendar, or should it sync the other valid events and report the skipped event? → A: Stop all changes for that run; report the feed issue and retry on the next run.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Keep the family calendar current (Priority: P1)

The user wants upcoming on-call shifts from Opsgenie to appear in the family's shared Google Calendar and stay current as the schedule changes.

**Why this priority**: The primary value is that the family can see the current on-call schedule without checking a separate calendar.

**Independent Test**: Provide a sample Opsgenie calendar feed and an authorized test Google Calendar, run a sync, and confirm that each upcoming source shift appears once with the correct time and details.

**Acceptance Scenarios**:

1. **Given** an upcoming shift exists in Opsgenie but not in the family calendar, **When** a sync completes, **Then** the shift appears in the family calendar.
2. **Given** a source shift's time or details change, **When** a sync completes, **Then** the matching calendar entry reflects the source change without creating a duplicate.
3. **Given** a future shift is removed from a successfully retrieved and parsed Opsgenie feed, **When** a sync completes, **Then** the corresponding sync-managed entry is removed from the family calendar.
4. **Given** a sync-managed shift has ended, **When** it is no longer present in the feed, **Then** its calendar entry remains as history.

### User Story 2 - Run unattended with one-time authorization (Priority: P1)

The user wants the sync to run automatically each day on an existing always-on machine after authorizing the Google account that can edit the family calendar.

**Why this priority**: Daily automation removes the need to maintain the calendar manually while fitting the user's existing home-server setup.

**Independent Test**: Complete authorization once, run the sync on consecutive days without an interactive sign-in, and confirm the second run can still read the source and update the destination.

**Acceptance Scenarios**:

1. **Given** the Google account has authorized the sync and can edit the target calendar, **When** the scheduled daily run starts, **Then** it completes without asking the user to sign in again.
2. **Given** Google authorization is revoked or expires, **When** a run cannot authenticate, **Then** no calendar changes are made and the run reports that authorization must be renewed.
3. **Given** a sync run completes, **When** the user checks its result, **Then** the output shows success or failure and counts of added, updated, and removed events.

### User Story 3 - Protect unrelated family events and private setup (Priority: P1)

The user wants the sync to manage only the on-call entries it created and keep private feed addresses and authorization credentials out of the public repository.

**Why this priority**: The target calendar contains family events, and the public repository must not expose private access details.

**Independent Test**: Place unrelated events and sync-managed events in a test calendar, run synchronization and failure scenarios, and confirm only sync-managed entries change and no private values appear in tracked files or output.

**Acceptance Scenarios**:

1. **Given** a family event was not created by the sync, **When** the sync runs, **Then** that event is not changed or deleted.
2. **Given** a user edits or deletes a sync-managed event, **When** the next successful sync runs, **Then** the source version is restored in the destination.
3. **Given** a source feed cannot be fetched or parsed completely, **When** a sync runs, **Then** it makes no additions, updates, or deletions based on that incomplete run and reports the failure.
4. **Given** the repository is published, **When** its tracked files and normal logs are inspected, **Then** they contain no private calendar URLs, calendar identifiers, OAuth tokens, or account-specific details.
5. **Given** an upcoming source event is unparseable or has a missing or duplicate stable identifier, **When** a sync runs, **Then** it makes no Google Calendar changes and reports the feed issue.

### Edge Cases

- The source feed is temporarily unavailable, empty, or malformed; the sync must not interpret it as mass deletion.
- The destination calendar is unavailable or the authorized account loses edit permission; the run must report failure without claiming a successful sync.
- Google authorization is revoked or requires user interaction again; the run must stop before changing events.
- A previously sync-managed future event is manually edited or removed in Google; the next successful sync restores the Opsgenie version.
- A shift has passed and disappears from a rolling source feed; its destination entry is retained as history.
- Any upcoming source event is malformed, has no stable identity, or duplicates another event identity; the entire run must stop before making Google Calendar changes and report the feed issue.
- A daily run is repeated with no source changes; it must not create duplicate events.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The sync MUST read on-call events from a user-configured Opsgenie iCalendar feed and write corresponding entries to a user-selected family Google Calendar.
- **FR-002**: The sync MUST run unattended at least once every 24 hours when scheduled by the user's existing always-on machine.
- **FR-003**: The user MUST be able to authorize a Google account with edit access to the target calendar through an interactive setup step; routine scheduled runs MUST use the saved authorization without interactive sign-in.
- **FR-004**: The sync MUST add missing upcoming source events and update matching sync-managed destination events when source details change.
- **FR-005**: The sync MUST identify its own destination events so it can update or remove them while leaving all events it did not create unchanged.
- **FR-006**: The sync MUST remove a future sync-managed destination event when that event has been removed from a successfully retrieved and completely parsed source feed.
- **FR-007**: The sync MUST retain past sync-managed destination events as calendar history after they fall outside the source feed's current window.
- **FR-008**: The sync MUST treat Opsgenie as authoritative; changes made manually to sync-managed destination events MUST be corrected on a later successful run. Changes to unrelated events MUST remain untouched.
- **FR-009**: If the source feed cannot be retrieved, is empty, cannot be completely parsed, or contains an upcoming event with a missing or duplicate stable identity, the sync MUST make no destination changes based on that run and MUST report a failure.
- **FR-010**: If Google authorization, target calendar access, or destination updates fail, the sync MUST report failure and MUST NOT report that run as successfully synchronized.
- **FR-011**: Private source URLs, destination calendar identifiers, OAuth credentials, and tokens MUST be supplied outside tracked public files, excluded from logs, and omitted from sample configuration except as nonfunctional placeholders.
- **FR-012**: The user MUST be able to determine from each run's output whether synchronization succeeded or failed and how many events were added, updated, or removed.

### Key Entities *(include if data involved)*

- **Source shift**: An on-call event from the configured Opsgenie calendar feed, including its stable identity, timing, and available descriptive details.
- **Sync-managed event**: A Google Calendar event created by this sync and tracked so later runs can update or remove it safely.
- **Sync run**: One scheduled or manual reconciliation attempt, with a success or failure result and counts of changes made.
- **Private configuration and authorization**: The feed address, target calendar selection, and credentials needed to access the user's calendars; these are local deployment data, not public project content.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After a successful scheduled run, every upcoming shift in the successfully read source feed is represented once in the target calendar.
- **SC-002**: When daily runs succeed, source additions, changes, and removals are reflected within 24 hours of becoming available in the source feed.
- **SC-003**: Repeating a sync with unchanged source data creates zero duplicate on-call events.
- **SC-004**: Across successful and failed sync runs, zero calendar events not created by the sync are changed or deleted.
- **SC-005**: In source retrieval, parsing, or authorization failure scenarios, zero destination changes are made based on incomplete source data or failed authorization.
- **SC-006**: After the one-time authorization step, at least 30 consecutive daily runs can complete without interactive sign-in, unless the user revokes authorization or Google requires reauthorization.
- **SC-007**: Inspection of the public repository and normal run output finds zero private feed addresses, calendar identifiers, authorization tokens, or account-specific details.

## Assumptions

- The user operates one Opsgenie schedule feed and selects one existing family Google Calendar where their account has permission to make changes.
- The source feed provides stable event identifiers and a complete view of the upcoming schedule it publishes. Planning must verify the feed's identity and rolling-window behavior before relying on absence to delete future events.
- Past on-call events should remain in the shared calendar for history.
- The sync is for the user's personal deployment; the public repository contains reusable code and placeholder configuration only.
- The authorization may need to be repeated if revoked or invalidated; the scheduled job must make this condition visible.
