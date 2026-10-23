<!--
Sync Impact Report
- Version change: scaffold → 1.0.0 (initial constitution)
- Modified principles: none
- Added sections: Core Principles; Project Constraints; Development Workflow; Governance
- Removed sections: none
- Follow-up TODOs: confirm original ratification date
-->

# Opsgenie Google Calendar Sync Constitution

## Core Principles

### I. Specification-Driven Development
New features and significant changes MUST follow the Spec Kit workflow. The active
specification and plan define intended behavior and technical direction before
implementation begins. This keeps calendar synchronization behavior reviewable and
consistent across changes.

### II. Approval Before Planning and Implementation
The specification MUST be approved before planning begins, and the implementation
plan MUST be approved before coding begins. Significant architectural decisions
require approval. This ensures product and architecture choices are settled before
they become costly to change.

### III. Small, Reviewable Changes
Implementation MUST proceed in small increments that can be reviewed independently.
Each increment MUST remain within its approved specification and plan. This limits
the scope of regressions and makes review practical.

### IV. Automated Verification
Automated tests MUST be run after code changes. Changes MUST comply with the
constitution and relevant specifications. Verification results MUST be reported
with the change so reviewers can assess its readiness.

### V. Repository Guidance Is Authoritative
The constitution is the project-wide source of governance principles;
feature-specific specifications and plans are the source of requirements and
design. Contributors MUST follow both, and MUST use the established Spec Kit
stages without repeating completed stages unnecessarily.

## Project Constraints

Project-specific technical, security, and operational constraints MUST be recorded
in the relevant specification or plan. No additional technology or deployment
constraints are established by this constitution.

## Development Workflow

For new features and significant changes, contributors MUST select the next
incomplete Spec Kit stage based on existing artifacts: Constitution, Specify,
Clarify when needed, Plan, Tasks, Analyze, Implement, and Converge. Minor bug fixes,
documentation updates, and trivial refactoring MAY bypass the full workflow, but
MUST still comply with this constitution. Automated tests MUST run after changes.

## Governance

This constitution governs project development practices. Amendments MUST update
this document and its version and dates, and MUST be reviewed before implementation
work that depends on the amendment proceeds. Version numbers follow semantic
versioning: MAJOR for incompatible governance changes, MINOR for new or materially
expanded principles or sections, and PATCH for clarifications and non-semantic
wording changes.

Every change MUST be reviewed for compliance with this constitution and its
applicable specification and plan. Deviations MUST be documented and approved
before implementation. Constitution compliance review is part of the normal
specification, plan, and implementation review process.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): original adoption date unknown | **Last Amended**: 2026-10-23
