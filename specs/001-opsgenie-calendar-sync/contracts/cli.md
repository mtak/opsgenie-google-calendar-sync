# CLI Contract: Opsgenie Calendar Sync

## Commands

### `authorize`

Starts the one-time Google desktop OAuth consent flow, opens a browser on the authorization machine, and stores the resulting refresh token in `~/.config/opsgenie-google-calendar-sync/token.json`.

- Requires a configured OAuth desktop client file outside the repository.
- Requires a browser-capable machine for the loopback authorization callback.
- Must not print the refresh token or write it into a tracked project file.
- Exits nonzero and reports a sanitized error if consent or token persistence fails.

### `sync`

Fetches and validates the Opsgenie feed, then reconciles upcoming shifts with the configured Google Calendar.

- Requires the private feed URL, destination calendar ID, and saved OAuth token.
- Makes no destination changes if feed retrieval or full validation fails.
- Operates only on events marked with this application's private sync property.
- Writes a summary containing outcome and added/updated/removed counts.
- Exits zero only on a complete successful run; exits nonzero for validation, authorization, access, or write failures.

## Configuration

The default private configuration is `~/.config/opsgenie-google-calendar-sync/config.toml`. It contains:

- Opsgenie iCalendar feed URL
- Google Calendar ID
- OAuth desktop client file path (default `oauth-client.json`)
- OAuth refresh-token file path (default `token.json`)

A checked-in `config.example.toml` may document key names using nonfunctional placeholder values only. Real values and token files stay outside tracked files and are excluded from output. The config directory is mounted read-only for scheduled sync runs.
