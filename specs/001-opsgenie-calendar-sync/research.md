# Research: Opsgenie Calendar Sync

**Date**: 2026-10-23
**Scope**: Authorization, source feed behavior, event identity, reconciliation, and daily execution for a single personal deployment.

## Google account authorization

**Decision**: Use Google's OAuth 2.0 installed desktop app flow for the single personal user. Run an explicit `authorize` command once on a browser-capable machine and protect the resulting refresh token outside the repository. Scheduled runs refresh access without an interactive login.

**Rationale**: Google supports installed desktop applications, recommends PKCE, and provides refresh tokens for unattended use. Desktop client credentials are public-client credentials and do not protect a shared secret; the refresh token is the sensitive value. The user avoids service accounts, domain-wide delegation, a hosted callback service, and a continuously running cloud workload.

**Consent screen constraint**: Do not leave the OAuth app in Testing for unattended daily use because Google's test-user authorizations expire after seven days. For personal use under 100 users, Google says verification is not required, though an unverified-app warning remains. The personal deployment should use production publishing status and accept that warning. Reauthorization remains necessary if the user revokes or Google invalidates the refresh token.

**Scope decision**: Check the target calendar owner before choosing a scope. `calendar.events.owned` permits event access on calendars the authorized account owns. If the target is shared with the account but owned by someone else, `calendar.events` may be needed; it covers events across calendars the account can access. Use the narrowest scope compatible with the actual target.

**Alternatives considered**:
- Google Calendar Secret iCal address: rejected because it is read-only and cannot create, update, or delete destination events.
- Service account: rejected for this personal setup because it adds Cloud IAM/service-account key setup and sharing; it does not remove the need to store a powerful credential securely.
- Shared public OAuth app: out of scope; the repository is public, but the deployment and OAuth client are for personal use.

**Sources**:
- Google, [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- Google, [Using OAuth 2.0](https://developers.google.com/identity/protocols/oauth2/)
- Google Cloud, [When verification is not needed](https://support.google.com/cloud/answer/13464323?hl=en-KI)
- Google Cloud, [Manage app audience and testing status](https://support.google.com/cloud/answer/15549945?hl=en-MC)
- Google, [Choose Calendar API scopes](https://developers.google.com/workspace/calendar/api/auth)
- Google Calendar Help, [Sync your calendar with computer programs](https://support.google.com/calendar/answer/37648?hl=en-ca)

## Opsgenie iCalendar feed

**Decision**: Treat a fully retrieved and parsed, non-empty feed as the source snapshot. Delete only future Google events carrying this application's private ownership marker when they are absent from that snapshot. Empty, malformed, incomplete, or identity-invalid snapshots cause no calendar changes. Preserve past destination events and all unmarked events.

**Rationale**: The user accepts source absence as a deletion signal for sync-managed future events. An application-owned private marker defines the only events eligible for mutation. A rolling feed can omit events outside its current window; the user's policy accepts deletion of managed future events absent from the current valid non-empty feed. Empty or invalid reads remain fail-closed.

**Alternatives considered**:
- Treat any event absent from an empty, failed, or invalid response as deleted: rejected because such a response is not an accepted source snapshot.
- Use a downloaded static export: rejected because the user needs periodic updates.

**Sanitized observation (2026-10-23)**: The user compared the feed around an upcoming schedule change and removal. Events have a UID field; the observed start and end times use Zulu (UTC) notation, and the event was within the feed window. The user reports that UIDs for all events change whenever the schedule changes. After removal, the event disappears without a cancellation or other removal marker.

**Deletion decision**: The user accepts deletion of future sync-managed events absent from a valid non-empty feed. UID churn does not expand deletion scope because Google Calendar events are selected by the private application marker. Reconciliation first matches by UID, then by normalized event fields to retain unchanged shifts when UIDs rotate; unmatched future managed events are deleted. Empty feeds remain a no-op. The rolling-window boundary was not measured; the user accepts source absence, including absence due to the feed's current window, as deletion for managed future events.

**Sources**:
- Atlassian Support, [Manage on-call schedules and rotations](https://support.atlassian.com/opsgenie/docs/manage-on-call-schedules-and-rotations/)
- Atlassian Support, [View your on-call schedule](https://support.atlassian.com/opsgenie/docs/view-your-on-call-schedule/)

## Google event ownership and metadata

**Decision**: Mark each created destination event with private extended properties containing an application marker and source UID. Search/list only marked events for reconciliation. Avoid a separate local database for this single calendar.

**Rationale**: Google documents private extended properties as hidden application-specific metadata on an event and supports listing events by a private extended-property query. This lets the sync find only its own events and survive container recreation without local database state.

**Alternatives considered**:
- Match by title/time: rejected because users can edit titles and multiple shifts can overlap or share the same summary.
- Local SQLite mapping: rejected for the first version because it adds mutable container state and backup concerns where Google event metadata suffices.
- Incremental sync token: not selected for the first version. Google does not allow a private extended-property filter together with `syncToken`; a complete scan of the small managed-event set is simpler and easier to reason about.

**Sources**:
- Google, [Extended properties](https://developers.google.com/workspace/calendar/api/guides/extended-properties)
- Google, [Events list reference](https://developers.google.com/workspace/calendar/api/v3/reference/events/list)
- Google, [Synchronize resources efficiently](https://developers.google.com/workspace/calendar/api/guides/sync)

## Daily execution

**Decision**: Use a one-shot Docker Compose command invoked by the host's cron. Do not add an internal scheduler or web service.

**Rationale**: The user already has an always-on machine and mentioned cron. A process that starts, reconciles once, reports a result, and exits is simpler to observe and restart. Persistent state is limited to private config and the OAuth refresh token, both mounted read-only where possible.

**Alternatives considered**:
- Always-running service with an internal daily timer: rejected because it adds lifecycle, health-check, and restart behavior without a user need.
- Public hosted job: rejected because it adds hosting, secret transfer, and deployment operations.

## Complexity assessment

The recurring runtime is small: host cron starts a container, the script reads one feed, lists marked events, applies changes, and exits. The initial Google setup is the main user effort: create/select a Cloud project, enable Calendar API, configure consent, create a Desktop OAuth client, authorize in a browser, and keep the OAuth app out of Testing. The refresh token must be transferred securely to a headless host if initial authorization is done elsewhere. Use `~/.config/oncall-calendar-sync/` for `config.toml`, `oauth-client.json`, and `token.json`; set directory permissions to 0700 and files to 0600. The public repository contains only a placeholder `config.example.toml`; the sync container mounts the private directory read-only. No Cloud-hosted runtime or database is needed.
