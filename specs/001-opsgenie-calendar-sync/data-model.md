# Data Model: Opsgenie Calendar Sync

## Source Shift

Represents one event read from the configured Opsgenie iCalendar feed.

| Field | Meaning | Validation |
| --- | --- | --- |
| source_uid | Current identity from the iCalendar `UID` | Required and unique within each feed snapshot; it may change across schedule edits |
| start | Inclusive event start | Required; preserve source time and timezone semantics |
| end | Exclusive event end | Required and later than start |
| summary | Event title, if present | Optional source text; do not include in routine logs |
| description | Event detail, if present | Optional source text; do not include in routine logs |
| location | Event location, if present | Optional source text; do not include in routine logs |
| status | Source event state, if represented | Canceled entries are treated according to verified feed behavior |

## Sync-Managed Google Event

Represents a destination event created by this application.

| Field | Meaning | Validation |
| --- | --- | --- |
| google_event_id | Google Calendar event identifier | Assigned by Calendar API |
| sync_marker | Private property identifying this application's events | Required on every created event |
| source_uid | Current UID of the source shift | Stored for matching and diagnostics; normalized event fields provide a fallback when the UID rotates |
| start/end/summary/description/location | Fields copied from the normalized source shift | Updated from Opsgenie on successful runs |
| destination_status | Current Google event state | Deleted only when it is future-dated, marked as managed, and safely absent from a complete source snapshot |

The sync marker and source UID are stored as Google Calendar private extended properties. The marker defines ownership and is required before any update or deletion. Do not store OAuth tokens or the source feed URL in event metadata.

## Private Runtime Configuration and Authorization

Contains the source feed URL, target calendar identifier, OAuth desktop client data, and refresh token. The default directory is `~/.config/oncall-calendar-sync/`, containing `config.toml`, `oauth-client.json`, and `token.json`. These values are provided by the operator on the deployment machine and are not committed to source control. The OAuth refresh token is treated as a credential; set the directory to mode 0700 and files to mode 0600. The scheduled container receives a read-only bind mount.

## Sync Run Result

| Field | Meaning |
| --- | --- |
| outcome | `success`, `partial_failure`, or `failure` |
| added_count | Number of events added during this run |
| updated_count | Number of events updated during this run |
| removed_count | Number of future managed events removed during this run |
| error_category | Sanitized category such as source_fetch, source_validation, authorization, permission, or calendar_write |

Run output must not include private input values or event details. A partial Calendar API failure must not be reported as full success; a retry must be safe and idempotent.

## Relationships

- One sync run reads one source feed and targets one calendar.
- A source shift maps to at most one sync-managed Google event by current source UID, with normalized event fields used to preserve matches when UIDs rotate.
- Only a valid non-empty source snapshot can authorize deletion; only unmatched future events with the private sync marker are deleted.
- A Google Calendar can contain both sync-managed and unrelated family events; the application may modify only events carrying its own sync marker.
