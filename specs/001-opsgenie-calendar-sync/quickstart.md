# Quickstart: Opsgenie Calendar Sync

## Prerequisites

- Python 3.12 or later for the one-time authorization setup.
- Docker Compose and cron on the always-on Linux host.
- An Opsgenie iCalendar URL and a Google account with edit permission on the chosen calendar.
- A Google Cloud project with Calendar API enabled and a Desktop app OAuth client.

## Private configuration

Create the private config directory and settings outside the repository:

```sh
mkdir -p "$HOME/.config/oncall-calendar-sync"
chmod 700 "$HOME/.config/oncall-calendar-sync"
cp config.example.toml "$HOME/.config/oncall-calendar-sync/config.toml"
chmod 600 "$HOME/.config/oncall-calendar-sync/config.toml"
```

Edit `config.toml` locally to set the real Opsgenie URL and Google Calendar ID. Keep the OAuth Desktop client as `oauth-client.json` in this directory and restrict it to mode 0600. Never put these values in tracked files, issue reports, or logs. Relative OAuth paths resolve from the config directory.

## One-time Google authorization

1. Enable the Google Calendar API in Google Cloud Console.
2. Configure the OAuth consent screen for personal use and publish it to Production; Google test-user refresh tokens expire after seven days.
3. Check calendar ownership and choose the narrowest compatible Calendar events scope. This implementation currently requests `calendar.events` because a shared calendar may be owned by another account.
4. Install the package on a browser-capable machine and run the interactive authorization command:

   ```sh
   python -m venv .venv
   . .venv/bin/activate
   pip install .
   oncall-calendar-sync authorize --config-dir "$HOME/.config/oncall-calendar-sync"
   ```

The command saves `token.json` with mode 0600. If authorization happens on a different machine, transfer the token securely and keep the directory private. Do not send the token in chat or commit it.

## First run and schedule

The feed comparison is documented below. The sync deletes future events absent from a valid, non-empty feed only when they carry its private ownership marker. Empty, failed, or invalid feeds cause no destination changes. Past events and unmarked events remain untouched.

Build and run against a dedicated test calendar first:

```sh
export ONCALL_SYNC_CONFIG_DIR="$HOME/.config/oncall-calendar-sync"
docker compose build
docker compose run --rm sync
```

Once the summary is successful and changes are verified in the dedicated test calendar, add a daily host cron entry:

```cron
0 6 * * * cd /path/to/oncall-calendar-sync && ONCALL_SYNC_CONFIG_DIR="$HOME/.config/oncall-calendar-sync" docker compose run --rm sync
```

The sync container receives the private directory read-only. Check its exit status and sanitized summary for failures. A revoked or invalid refresh token requires running `authorize` again. Do not select the family calendar for destructive tests.

## Feed behavior validation status

The sanitized feed comparison found that schedule changes appear to change UIDs across events, and a removed event disappears without a cancellation marker. The observed event used Zulu (UTC) times and was inside the feed window. The sync accommodates UID rotation by matching unchanged normalized event details. Per the user's policy, absence from a valid non-empty feed removes unmatched future events carrying the private ownership marker. Empty feeds remain a no-op; malformed or failed reads also cause no changes. Past and unmarked events are preserved.

## Local performance check

On 2026-10-23, reconciliation of 300 synthetic shifts through an in-memory fake Calendar gateway took 0.0023 seconds on the first run (300 additions) and 0.0025 seconds on a repeated run (0 updates, 0 removals). This checks local reconciliation cost only; it does not measure Google API latency.

On 2026-10-23, the full unit suite passed (59 passed; 2 opt-in tests skipped when integration mode was off), `docker compose config` passed with a placeholder config-directory path, and both opt-in Google Calendar integration tests passed against the dedicated test calendar in 5.03 seconds. The integration tests create temporary marked and unmarked events and clean them up afterward. Do not use the family calendar for this check.
