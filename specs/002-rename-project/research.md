# Research: Rename the Project

## Decision: Use one canonical identity across the distribution, module, CLI, config, container, and repository

**Rationale**: The feature specification requires the new name across project identity, code, defaults, and documentation. Use `opsgenie-google-calendar-sync` for the distribution, command, config directory, container command, user-agent product token, and repository; use `opsgenie_google_calendar_sync` for the Python import package and directory. Rename the config override variable to `OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR` so new setup instructions and container configuration use the same identity.

**Alternatives considered**: Keep the old Python import package or environment variable for compatibility. Rejected because the user confirmed there are no current users and asked to rename the code and project references; the user's own local installation migration is explicitly out of scope.

## Decision: Use separate canonical distribution, command, and import-package spellings

**Rationale**: Python packaging distinguishes a distribution name from an import package name. The distribution and generated console command use `opsgenie-google-calendar-sync`; Python imports use `opsgenie_google_calendar_sync`. The console script entry point must point to the renamed package's `cli:main`. This follows the existing packaging model without changing runtime dependencies.

**Alternatives considered**: Use the hyphenated distribution name as a Python import name. Rejected because Python import identifiers use underscores for this package naming convention.

**External references**: [Distribution package vs. import package — PyPA](https://packaging.python.org/en/latest/discussions/distribution-package-vs-import-package/); [Entry points specification — PyPA](https://packaging.python.org/en/latest/specifications/entry-points/)

## Decision: Rename the existing repository in place, then update the primary checkout remote

**Rationale**: The repository owner is `mtak`, and the current remote is `https://github.com/mtak/oncall-calendar-sync.git`. GitHub documents that renaming a repository redirects existing web links and Git operations, while recommending updating local clones to the new URL. The planned canonical URL is `https://github.com/mtak/opsgenie-google-calendar-sync.git`. Only the primary local checkout is renamed; auxiliary worktree paths, branches, contents, and remotes stay unchanged, with pointer repair only to preserve their connections.

**Alternatives considered**: Create a second repository and copy the project. Rejected because an in-place rename preserves the repository identity and GitHub's documented redirects.

**External reference**: [Renaming a repository — GitHub Docs](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)

## Finding: Moving the main checkout can require repairing linked-worktree connections

Git documents that the main working tree cannot be moved with `git worktree move`; after manually moving the main worktree, `git worktree repair` can reestablish its connections with linked worktrees. The user excludes changes to auxiliary worktree paths, branches, contents, and remotes, while allowing minimal metadata repair to preserve their connections.

**External reference**: [git-worktree documentation](https://git-scm.com/docs/git-worktree)

## Decision: Repair only linked-worktree administrative pointers after moving the primary checkout

**Rationale**: The user approved pointer repair while keeping auxiliary worktree paths, branches, contents, and remotes unchanged. Git's documented `git worktree repair` command is specifically intended to reconnect linked worktrees after the main worktree has been moved manually.

**Alternatives considered**: Leave pointer references stale or rename auxiliary worktrees. Rejected because stale pointers can prevent Git operations in those worktrees, while renaming them exceeds the user's selected scope.

## Decision: Resolve the canonical remote only in the primary worktree

**Rationale**: Git shares repository configuration across linked worktrees by default, and `remote.origin.url` is multi-valued when a per-worktree value is added alongside the shared value. A per-worktree `remote.origin.url` therefore leaves the primary checkout resolving both URLs. The user approved enabling the `worktreeConfig` extension; use its primary-worktree `url.<canonical>.insteadOf` rule to map the shared old URL to the canonical repository URL only in the primary checkout. Keep the common remote URL unchanged so auxiliary worktrees continue using it. This checkout has `core.bare=false` and no `core.worktree` value; Git requires moving existing `core.bare` and `core.worktree` values to the main worktree config when enabling the extension, so preserve `core.bare=false` in that config.

**Alternatives considered**: Change the shared `remote.origin.url`, which would update every linked worktree, or give each linked worktree its own remote configuration. Rejected because the user asked to keep auxiliary remote values and configuration unchanged.

**External references**: [git-worktree configuration documentation](https://git-scm.com/docs/git-worktree#_configuration_file); [Git URL rewrite configuration](https://git-scm.com/docs/git-config#Documentation/git-config.txt-urlltbasegtinsteadOf)

## Decision: Treat GitHub repository settings and the checkout directory as a separate operational phase

**Rationale**: A GitHub repository rename requires owner or repository administrator permission. GitHub says existing local Git operations continue through redirects, but recommends updating clone remotes. Separating this work from source changes gives a clear gate: complete and review code/docs first, rename the remote repository, update `origin`, then rename the primary checkout directory and verify it.

**Alternatives considered**: Rename GitHub before code and documentation changes. Rejected because it would leave the published project identity inconsistent during implementation and complicate review links.

## Decision: Keep synchronization contracts and private runtime data unchanged

**Rationale**: The specification explicitly excludes changes to synchronization rules, event contents, OAuth scopes, and the user's local installation. Only the documented default path for new installations changes. No database, schema, or migration is needed.

**Alternatives considered**: Add a runtime migration for the user's current installation. Rejected because the user stated they will handle that installation separately.

## Decision: Keep the private calendar-event ownership marker stable

**Rationale**: The existing reconciliation code uses the private Google Calendar extended-property name `oncallCalendarSync` and a `SYNC_MARKER` value to identify events created by this application. Changing either persisted identifier as part of a name-only change could make previously managed events invisible to reconciliation. Preserve both values and all event fields; rename only the CLI, package, and project-specific configuration and test environment variables.

**Alternatives considered**: Rename the calendar marker to match the new project name. Rejected because it changes persisted synchronization metadata and could cause duplicate events or prevent updates to existing managed events.
