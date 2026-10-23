# Development Guidelines

## Development Methodology

This project follows GitHub Spec Kit's Specification-Driven
Development (SDD) methodology.

For new features and significant changes, Codex MUST follow
the Spec Kit workflow using the installed skills.

### Workflow

1. Constitution — Establish project principles (once per project).
2. Specify — Define requirements and acceptance criteria.
3. Clarify — Resolve ambiguities where necessary.
4. Plan — Design the technical implementation.
5. Tasks — Break the plan into actionable tasks.
6. Analyze — Validate consistency between artifacts.
7. Implement — Execute tasks incrementally.
8. Converge — Verify implementation completeness.

Use the corresponding `$speckit-*` skills for each stage.

Automatically select the appropriate next stage based on
existing artifacts. Do not restart completed stages unnecessarily.

## Source of Truth

- Constitution: `.specify/memory/constitution.md`
- Specifications and plans: `specs/`
- Spec Kit skills: `.agents/skills/`

Always follow the constitution and relevant specifications.

## Human Oversight

- Require approval of specifications before planning.
- Require approval of implementation plans before coding.
- Implement in small, reviewable increments.
- Run automated tests after changes.
- Never make significant architectural decisions without approval.

## Exceptions

Minor bug fixes, documentation updates, and trivial refactoring
may bypass the full SDD workflow.

All changes must still comply with the constitution.
