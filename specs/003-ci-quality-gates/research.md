# Research: CI Quality Gates

## Decision 1: Use GitHub Actions for repository checks

- **Decision**: Define checks as a GitHub Actions workflow triggered for pull requests targeting `main` and pushes to `main`.
- **Rationale**: The project is hosted on GitHub and needs visible pull request status checks. GitHub Actions supports event and branch filters directly in workflow configuration.
- **Alternatives considered**: External CI services would add a second provider and additional repository configuration without a project need.
- **References**: [GitHub workflow triggers](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow).

## Decision 2: Expose lint, test, and build as separate required checks

- **Decision**: Use distinct jobs with stable names for lint, tests, and package build; configure the main branch protection rule to require all three job checks.
- **Rationale**: Separate results make failures easier to identify and allow the branch rule to require each result. GitHub documents required status checks as a merge protection rule.
- **Alternatives considered**: A single combined job would be simpler but would expose one aggregate status and make individual check results less clear. Advisory-only results are rejected because the approved clarification requires passing checks before merge.
- **References**: [GitHub ruleset status checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) and [creating repository rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository).

## Decision 3: Keep the lint baseline modest and shared

- **Decision**: Configure Ruff in `pyproject.toml`, begin with the Ruff’s default error and undefined-name rule families (`E4`, `E7`, `E9`, and `F`), and expose Ruff through the existing development extra alongside pytest.
- **Rationale**: A shared configuration lets contributors run the same lint check locally and in CI. The initial rules catch common mistakes without requiring broad reformatting.
- **Alternatives considered**: A separate configuration file duplicates Python project settings; adding a formatter, type checker, or many extra rule families expands scope beyond the approved baseline.
- **References**: [Ruff configuration](https://docs.astral.sh/ruff/configuration/).

## Decision 4: Build the distribution as an independent check

- **Decision**: Have the build job produce a wheel and source distribution from the project metadata without uploading them.
- **Rationale**: A package build checks that the installable project metadata and source layout can produce distributable artifacts. The Python Packaging User Guide documents building distributions as a packaging validation step.
- **Alternatives considered**: Testing only an editable install can miss distribution build failures; publishing artifacts is outside the feature scope.
- **References**: [Python Packaging User Guide: Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

## Decision 5: Use the declared Python baseline and read-only workflow permissions

- **Decision**: Run checks on Python 3.12, matching `requires-python`, and grant the workflow only read access to repository contents.
- **Rationale**: An explicit interpreter avoids runner-default drift. The Python setup action recommends setting a Python version explicitly and using `contents: read` for checkout-based workflows.
- **Alternatives considered**: A version matrix is unnecessary while the project declares only a minimum Python version and does not claim a wider tested-version matrix.
- **References**: [`actions/setup-python` documentation](https://github.com/actions/setup-python).
