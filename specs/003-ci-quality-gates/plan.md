# Implementation Plan: CI Quality Gates

**Branch**: `003-ci-quality-gates` | **Date**: 2026-10-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-ci-quality-gates/spec.md`

## Summary

Add pull request and main-branch CI with distinct Ruff lint, pytest, and package-build checks. Require those three status checks for merges to `main`. Keep lint rules modest and configured in the existing `pyproject.toml`, use the project's declared Python 3.12 baseline, grant the workflow read-only repository access, and correct all stale README invocations to match the executable declared in package metadata.

## Technical Context

**Language/Version**: Python 3.12, matching `requires-python = ">=3.12"`.

**Primary Dependencies**: Existing Python package dependencies; pytest is already in the `dev` extra. Add Ruff to the development extra and use the Python packaging `build` frontend in CI for distribution validation.

**Storage**: No application storage. CI build artifacts are temporary and are not published.

**Testing**: Existing pytest suite, Ruff linting, and wheel/source distribution build. Existing tests use fixtures and mocked Google Calendar calls, so no real credentials should be needed.

**Target Platform**: GitHub Actions on a Linux runner; GitHub repository ruleset or branch protection for `main`.

**Project Type**: Python command-line application with a `src/` package and pytest suite.

**Performance Goals**: No strict runtime target. Keep checks independent and avoid matrix expansion beyond the declared Python 3.12 baseline.

**Constraints**: Run on pull requests targeting `main` and pushes to `main`; provide stable job names for merge protection; use only read permissions; do not use deployment secrets or real calendar access; avoid repository-wide formatting changes and type-checking scope.

**Scale/Scope**: One workflow, three check jobs, a small Ruff configuration, development dependency update, README command correction, and repository merge-protection configuration.

## Constitution Check

- **I. Specification-Driven Development**: PASS. This plan follows the approved and clarified specification.
- **II. Approval Before Planning and Implementation**: PASS. The user approved the specification before planning. Coding remains gated on approval of this plan.
- **III. Small, Reviewable Changes**: PASS. Workflow, lint configuration/dependency, documentation correction, and merge protection are separable review points.
- **IV. Automated Verification**: PASS. The plan defines the test, lint, and distribution-build checks that run after implementation changes.
- **V. Repository Guidance Is Authoritative**: PASS. The scope follows `specs/003-ci-quality-gates/spec.md`; no sync behavior changes are planned.

**Gate result**: PASS. No constitution violations identified.

## Project Structure

### Documentation (this feature)

```text
specs/003-ci-quality-gates/
├── plan.md
├── research.md
├── data-model.md
├── contracts/
│   └── ci.md
├── quickstart.md
└── tasks.md                 # Generated in the next Spec Kit stage
```

### Source Code (repository root)

```text
.github/
└── workflows/
    └── quality.yml          # Pull request and main-branch checks

pyproject.toml                # Ruff settings and development dependency
README.md                     # Correct installed executable name
src/opsgenie_google_calendar_sync/
tests/
```

**Structure Decision**: This is a repository-level quality automation change in the existing Python CLI project. Add one GitHub Actions workflow, extend existing project metadata, and fix the README command references. No application source layout changes are required. Configure `main` branch protection or a repository ruleset to require the three stable check contexts (`Quality / lint`, `Quality / tests`, and `Quality / build`) after the workflow has reported them once.

## Phase 0: Research Findings

See [research.md](research.md). GitHub Actions is selected because the repository is hosted on GitHub. Separate stable jobs provide independently visible required status checks. Ruff starts with Ruff’s standard error and undefined-name rule families (`E4`, `E7`, `E9`, and `F`); package validation builds wheel and source distribution artifacts without publishing.

## Phase 1: Design

- [Data model](data-model.md) describes check runs and the README command reference; no runtime application data is added.
- [CI contract](contracts/ci.md) defines triggers, job names, permissions, runtime, and required outcomes.
- [Quickstart](quickstart.md) gives local commands and a repository-level verification checklist.

## Constitution Check (Post-Design)

- **I. Specification-Driven Development**: PASS. Design artifacts trace to the approved feature requirements.
- **II. Approval Before Planning and Implementation**: PASS. The implementation remains gated on user approval of this plan.
- **III. Small, Reviewable Changes**: PASS. The design keeps changes localized to workflow, project metadata, README, and repository rules.
- **IV. Automated Verification**: PASS. The workflow itself will verify lint, tests, and package build.
- **V. Repository Guidance Is Authoritative**: PASS. The CI checks do not alter synchronization behavior or private deployment setup.

**Post-design gate result**: PASS.

## Complexity Tracking

No constitution violations. Three independent checks are needed to satisfy the approved merge-gate requirement while making failures diagnosable. No additional checker, database, or application architecture is introduced.
