# Quickstart: Validate CI Quality Gates

## Prerequisites

- Python 3.12 or later
- GitHub Actions enabled for the repository
- Permission to configure branch protection or a repository ruleset for `main`

## Run Checks Locally

From the repository root:

```bash
python -m pip install -e '.[dev]'
ruff check .
pytest
python -m pip install build
python -m build
```

Expected results: Ruff and pytest exit successfully, and `python -m build` creates a wheel and source distribution in `dist/`.

## Validate Pull Request Behavior

1. Open or update a pull request targeting `main`.
2. Confirm that `Quality / lint`, `Quality / tests`, and `Quality / build` each appear and complete.
3. Confirm the repository's branch protection or ruleset requires all three status checks before merge.
4. Confirm a failed or incomplete required check blocks merging.
5. Push a commit to `main` and confirm the same checks run.

## Validate the README Command

Compare the executable configured in `[project.scripts]` in `pyproject.toml` with each command example and the CLI reference in `README.md`. They must match exactly.

No live calendar, source feed, OAuth client, or token is needed for these checks.

## Local Verification Record

Verified in the task worktree with Python 3.14.4:

- `ruff check .` passed.
- `pytest` passed: 59 passed; 2 opt-in Google Calendar integration tests skipped.
- `python -m build` produced both the wheel and source distribution.
- `opsgenie-google-calendar-sync --help` displayed the documented executable name.
- Workflow YAML passed `yamllint` with the relaxed GitHub-compatible profile.

The local environment did not provide Python 3.12, so the exact CI interpreter baseline is configured in the workflow but has not been run locally. The repository merge rule is not active yet: it must be configured after these workflow check contexts are available in GitHub.
