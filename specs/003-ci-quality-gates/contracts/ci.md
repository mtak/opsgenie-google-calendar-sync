# CI Contract

## Workflow Triggers

- Run for pull requests targeting `main`.
- Run for commits pushed to `main`.
- Do not require secrets or access to a live Google Calendar.

## Required Status Checks

The `Quality` workflow exposes these stable check contexts, all of which must pass before a pull request can merge:

- `lint`
- `tests`
- `build`

A missing, cancelled, or failed required check does not satisfy the merge gate.

## Check Responsibilities

| Check | Required behavior |
|---|---|
| `lint` | Run the configured Ruff rules over the project. |
| `tests` | Install project development dependencies and run the complete pytest suite. |
| `build` | Build wheel and source distribution artifacts from the project metadata; do not publish them. |

## Runtime and Permissions

- Use Python 3.12, matching the declared project baseline.
- Grant only read access to repository contents.
- Do not expose or request deployment credentials.

## README Command Contract

README command examples and the CLI reference must use the executable name declared under `[project.scripts]` in `pyproject.toml`.
