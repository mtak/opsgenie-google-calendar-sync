# Quickstart: Opsgenie Calendar Sync

This guide describes the intended first-run and daily-operation flow and the proposed private configuration layout. Exact commands will be finalized during implementation.

## Prerequisites

- An Opsgenie iCalendar URL for the intended on-call schedule.
- A Google account with permission to edit the family calendar.
- A Google Cloud project, either existing or created for this personal app.
- Docker Compose and cron on the always-on Linux machine.
- A browser-capable machine for the one-time desktop OAuth authorization.

## Google authorization setup

1. In Google Cloud Console, select or create a project and enable the Google Calendar API.
2. Configure the OAuth consent screen for the account that will authorize the sync. For personal use under 100 users, verification is not required, but Google may show an unverified-app warning.
3. Set the app's publishing status to Production instead of leaving it in Testing; testing authorizations expire after seven days.
4. Create an OAuth client of type Desktop app and download its client configuration to a private location outside the repository.
5. Check who owns the family calendar. Authorize an account with edit access and select the narrowest supported event scope for that ownership/access model.
6. Run the `authorize` command on a machine with a browser. It will open Google's consent page and save a refresh token to a private file.
7. If authorization occurs on a different machine from the always-on host, transfer the token file securely and restrict its file permissions. Do not send it in chat or commit it.

## Private sync configuration

Create `~/.config/oncall-calendar-sync/` on the machine that will run cron. Store three files there:

- `config.toml`: Opsgenie feed URL, Google Calendar ID, and paths to the OAuth files.
- `oauth-client.json`: the downloaded Desktop app OAuth client configuration.
- `token.json`: the refresh token produced by the one-time authorization.

The public `config.example.toml` will contain only nonfunctional placeholders, in this shape:

```toml
source_ical_url = "https://example.invalid/replace-me.ics"
target_calendar_id = "replace-with-calendar-id"
oauth_client_file = "oauth-client.json"
oauth_token_file = "token.json"
```

Resolve relative OAuth file paths from the directory containing `config.toml`. Set the directory permissions to 0700 and each file to 0600. If authorization was performed on another machine, copy the private directory to the always-on host over a secure channel. Set `ONCALL_SYNC_CONFIG_DIR` in the host environment or cron to point to this directory. Docker Compose mounts it read-only into the scheduled container. No real config, feed URL, calendar ID, OAuth file, or token belongs in the repository.

## First sync and daily schedule

1. Validate that the configured feed can be fetched and parsed and includes stable UIDs. Use sanitized local samples for development; never commit the actual feed URL or captured private calendar contents.
2. Run the sync manually once and confirm its status/count summary and the resulting events in a dedicated test calendar before selecting the family calendar for real use.
3. Add a host cron entry that runs the Compose job once daily, for example at 06:00 local host time:

   ```cron
   0 6 * * * cd /path/to/oncall-calendar-sync && ONCALL_SYNC_CONFIG_DIR="$HOME/.config/oncall-calendar-sync" docker compose run --rm sync
   ```

4. Check cron's exit status or sanitized logs for failures. If authorization has been revoked or invalidated, repeat the browser authorization step.

## Safety checks before enabling deletions

Opsgenie documentation does not guarantee stable iCalendar UIDs or document how removed shifts appear in the feed. Before relying on feed absence for deletion, compare sanitized feed samples from before and after a shift change and removal. The sync must retain past entries, and an empty or invalid feed must never be treated as a complete deletion snapshot.
