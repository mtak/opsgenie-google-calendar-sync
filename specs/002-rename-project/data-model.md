# Data Model: Rename the Project

This change does not add or alter runtime data. Configuration values, OAuth credentials, and calendar events keep their existing formats and behavior. The entities below describe project identity and checkout state used to verify the rename.

## Project Identity

| Attribute | Before | Canonical after rename | Validation |
|---|---|---|---|
| Distribution and executable | `oncall-calendar-sync` | `opsgenie-google-calendar-sync` | Installed metadata and command use the canonical name. |
| Python import package | `oncall_calendar_sync` | `opsgenie_google_calendar_sync` | Source package and test imports use the canonical name. |
| Default configuration directory | `~/.config/oncall-calendar-sync` | `~/.config/opsgenie-google-calendar-sync` | Default path function resolves to the canonical directory. |
| Configuration override variable | `ONCALL_SYNC_CONFIG_DIR` | `OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR` | Application, Docker, Compose, and setup docs agree. |
| GitHub repository | `mtak/oncall-calendar-sync` | `mtak/opsgenie-google-calendar-sync` | Repository page and primary checkout `origin` use the canonical URL. |
| Primary checkout directory | `~/dev/oncall-calendar-sync` | `~/dev/opsgenie-google-calendar-sync` | The renamed primary checkout resolves to the canonical path. |

## Primary Checkout

The primary checkout is the local working copy at the path above. Its source tree, tracked and untracked files, Git history, active branch, and local installation data are not redesigned by this feature. The directory move must preserve the checkout's contents. Its effective `origin` URL resolves to the canonical repository through primary-worktree-specific URL rewriting while the shared remote URL stays unchanged for auxiliary worktrees. Auxiliary worktree paths, branches, contents, and remotes remain unchanged; repair Git's administrative pointers only if needed to preserve their connection to the moved primary checkout.

## Runtime Configuration and Calendar Data

The configuration continues to contain the source iCalendar URL, target calendar ID, and OAuth client/token file references. Calendar events and their reconciliation lifecycle are unchanged, including the private event-ownership property name `oncallCalendarSync` and the `SYNC_MARKER` value used to recognize managed events. The user's current local installation path is not migrated by this feature.
