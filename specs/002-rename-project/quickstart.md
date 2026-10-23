# Rename Validation Quickstart

This guide validates a completed rename. It does not migrate the user's current local installation. Run code checks from the implementation checkout before performing the GitHub and primary-checkout rename.

## Prerequisites

- Python 3.12 and a Git version that supports the `worktreeConfig` extension are available.
- The project source changes have been applied in the implementation checkout.
- An owner or administrator can rename the GitHub repository for the external repository step.
- The GitHub CLI is authenticated to verify the renamed repository through its former private-repository path.

## Validate Package and CLI Names

From the project root, create an isolated environment and install the package with development dependencies:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
```

Confirm the canonical executable and configuration default:

```sh
opsgenie-google-calendar-sync --help
python -c 'from opsgenie_google_calendar_sync.config import default_config_dir; print(default_config_dir())'
```

Expected: help identifies `opsgenie-google-calendar-sync`; the path ends in `.config/opsgenie-google-calendar-sync`.

Run automated verification with the opt-in live Google Calendar integration flag disabled. This keeps verification isolated from calendar data:

```sh
env -u OPSGENIE_GOOGLE_CALENDAR_SYNC_INTEGRATION python -m pytest
```

Expected: unit tests pass and live-calendar integration tests are skipped. They require a dedicated disposable test calendar and are outside this rename validation.

Validate Docker Compose configuration with the canonical override name:

```sh
export OPSGENIE_GOOGLE_CALENDAR_SYNC_CONFIG_DIR="$HOME/.config/opsgenie-google-calendar-sync"
docker compose config
```

Expected: Compose resolves the config volume and sets the container's config path to `/run/oncall-config`.

## Validate GitHub and Primary Checkout

1. In GitHub repository settings, rename the existing repository to `opsgenie-google-calendar-sync`.
2. Configure URL rewriting only in the primary worktree while leaving auxiliary remotes unchanged. Git shares config by default; preserve the current `core.bare=false` behavior in the primary worktree config as required when enabling worktree-specific config:

```sh
git -C ~/dev/oncall-calendar-sync config --unset core.bare
git -C ~/dev/oncall-calendar-sync config extensions.worktreeConfig true
git -C ~/dev/oncall-calendar-sync config --worktree core.bare false
git -C ~/dev/oncall-calendar-sync config --worktree 'url.https://github.com/mtak/opsgenie-google-calendar-sync.git.insteadOf' https://github.com/mtak/oncall-calendar-sync.git
git -C ~/dev/oncall-calendar-sync remote get-url origin
```

Expected: the primary checkout resolves `origin` to the new URL. The shared remote URL remains `https://github.com/mtak/oncall-calendar-sync.git` for auxiliary worktrees.

3. From `~/dev`, rename the primary directory to `opsgenie-google-calendar-sync` without changing its contents.
4. Repair linked-worktree pointers from the moved primary checkout:

```sh
git -C ~/dev/opsgenie-google-calendar-sync worktree repair
```

This repairs Git's administrative connections only. It does not move auxiliary worktrees or change their branches, contents, or remotes.

5. Confirm the local location and remote, and verify the former private-repository URL resolves to the canonical repository:

```sh
git -C ~/dev/opsgenie-google-calendar-sync rev-parse --show-toplevel
git -C ~/dev/opsgenie-google-calendar-sync remote get-url origin
git -C ~/dev/opsgenie-google-calendar-sync ls-remote origin HEAD
gh repo view mtak/oncall-calendar-sync --json nameWithOwner,url
```

Expected: the root path is `~/dev/opsgenie-google-calendar-sync`, the remote is the canonical GitHub URL, `ls-remote` returns the repository's HEAD, and the former repository lookup reports `mtak/opsgenie-google-calendar-sync`. `git worktree list` should still report each auxiliary worktree at its original path.

Confirm a linked worktree still sees the shared old remote URL, which GitHub redirects to the renamed repository:

```sh
git -C /tmp/oncall-calendar-sync-worktrees/implementation remote get-url origin
```

Expected: `https://github.com/mtak/oncall-calendar-sync.git`.
