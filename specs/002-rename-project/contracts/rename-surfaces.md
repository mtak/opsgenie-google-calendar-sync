# Rename Surface Contract

This contract defines the names exposed to a new installation or contributor after the rename. Synchronization behavior and the `authorize`/`sync` command semantics do not change.

| Surface | Canonical value |
|---|---|
| Repository | `https://github.com/mtak/opsgenie-google-calendar-sync` |
| Python distribution | `opsgenie-google-calendar-sync` |
| Python import package | `opsgenie_google_calendar_sync` |
| Executable | `opsgenie-google-calendar-sync` |
| Default private config directory | `~/.config/opsgenie-google-calendar-sync` |
| Config directory override | `OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR` |
| Container entry point | `opsgenie-google-calendar-sync` |
| HTTP User-Agent product token | `opsgenie-google-calendar-sync/0.1` |
| Primary local checkout | `~/dev/opsgenie-google-calendar-sync` |

## CLI

The executable accepts the existing `authorize` and `sync` subcommands and the existing `--config-dir` option. The rename changes the executable's name and displayed program name only; exit behavior, synchronization behavior, and output privacy remain unchanged.

The private event property name `oncallCalendarSync` and the value format supplied by `SYNC_MARKER` remain unchanged so existing events continue to be recognized by synchronization.

## Repository and Checkout

Rename the existing repository in place under owner `mtak`. After the GitHub rename, the primary checkout's effective `origin` must resolve to the canonical repository URL through primary-worktree-specific URL rewriting, and the primary directory must use the canonical local path. Keep the shared `origin` URL unchanged so auxiliary worktrees retain their existing remote. Auxiliary worktree directories, branches, and contents remain unchanged; repair only the Git metadata pointers needed to keep them connected after the primary checkout moves.

## Compatibility Scope

No compatibility alias is required for the old distribution, import package, executable, or configuration override. There are no current users; migration of the user's current local installation is out of scope. References to the old name are allowed only where needed to explain this rename.
