# Data Model: CI Quality Gates

This feature introduces no persistent application data. It defines two review artifacts produced for each repository revision.

## Quality Check Run

- **Identity**: A workflow run associated with a pull request revision or a commit pushed to `main`.
- **Checks**: Lint, tests, and package build.
- **Result per check**: Passed, failed, or incomplete.
- **Merge relationship**: A pull request is eligible to merge only after all three required checks pass.
- **Private data**: The run uses sanitized tests and requires no real feed URL, calendar identifier, OAuth credentials, or Google Calendar access.

## Contributor Command Reference

- **Source of truth**: The installed executable declared by project installation metadata.
- **Occurrences**: README installation, authorization, sync, and CLI reference examples.
- **Validation rule**: Every documented invocation uses the same executable name as the package metadata.
