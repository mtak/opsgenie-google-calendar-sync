# Feature Specification: Rename the Project

**Feature Branch**: `002-rename-project`

**Created**: 2026-10-23

**Status**: Draft

**Input**: User description: "Rename the project from `oncall-calendar-sync` to `opsgenie-google-calendar-sync`, updating documentation and code, and coordinate renaming the GitHub repository and local checkouts."

## Clarifications

### Session 2026-10-23

- Q: Should the local rename cover only the primary checkout, or all local worktrees for this repository? → A: Only the primary checkout; auxiliary worktrees are out of scope.
- Q: May Git administrative pointers for auxiliary worktrees be repaired after moving the primary checkout? → A: Repair pointers only; keep their directories, branches, contents, and remotes unchanged.
- Q: May Git worktree-specific configuration be enabled so only the primary checkout uses the renamed repository URL? → A: Yes; use worktree-specific config and keep auxiliary worktree remotes unchanged.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Use the renamed project (Priority: P1)

An operator installs or runs the project under the name `opsgenie-google-calendar-sync` and follows the updated setup instructions to synchronize Opsgenie on-call events with Google Calendar.

**Why this priority**: The project name is the identity operators encounter when installing, configuring, and running the tool.

**Independent Test**: Follow the updated setup guide with a fresh configuration and confirm the documented command and configuration location are accepted by the project.

**Acceptance Scenarios**:

1. **Given** an operator following the current setup guide, **When** they install and invoke the project, **Then** the guide and user-facing command consistently identify it as `opsgenie-google-calendar-sync`.

### User Story 2 - Find and check out the renamed repository (Priority: P2)

A contributor finds the project at its renamed GitHub repository and uses a local checkout whose directory and remote point to the renamed repository.

**Why this priority**: Contributors need the canonical repository name and location to clone, update, and contribute to the project.

**Independent Test**: Open the renamed repository on GitHub, clone it into a directory named `opsgenie-google-calendar-sync`, and confirm that its configured remote uses the renamed repository URL.

**Acceptance Scenarios**:

1. **Given** the current GitHub repository, **When** the rename is completed, **Then** its canonical repository name and URL are `opsgenie-google-calendar-sync` and existing links to the former repository continue to reach it.
2. **Given** the primary local checkout on this machine and linked auxiliary worktrees, **When** the local rename is completed, **Then** the primary directory and remote use the canonical name, and auxiliary worktrees remain connected without changes to their directories, branches, contents, or remotes.
3. **Given** a contributor reading project documentation, **When** they follow repository, package, container, or command references, **Then** those references use the new project name, with the former name appearing only where necessary to describe the rename.

### Edge Cases

- The GitHub repository rename and local checkout update happen at different times. The rename steps must make the required order clear and leave the local remote pointing to the renamed repository.
- Moving the primary checkout can invalidate Git metadata pointers for linked worktrees. Repair only those pointers so the linked worktrees remain usable; preserve their directories, branches, contents, and remotes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The canonical project name MUST be `opsgenie-google-calendar-sync` in project documentation and user-facing project metadata.
- **FR-002**: The package installation name, executable command, and container entry point MUST use the canonical project name for new installations.
- **FR-003**: New installations MUST use a configuration location named for the canonical project.
- **FR-004**: Setup and operations documentation MUST use the new project name and explain how contributors find the renamed repository.
- **FR-005**: The GitHub repository MUST be renamed to `opsgenie-google-calendar-sync`, and the primary local checkout on this machine MUST be renamed to match and configured to use the renamed repository as its remote. If moving the primary checkout invalidates linked-worktree metadata pointers, those pointers MUST be repaired without changing auxiliary worktree directories, branches, contents, or remotes.
- **FR-006**: The rename MUST preserve synchronization behavior.
- **FR-007**: All references to the former name MUST be removed from active project identity, documentation, code, and defaults, except references needed to describe the rename itself.

### Key Entities

- **Project Identity**: The canonical name used by operators and contributors across documentation, installation, commands, containers, and repository location.
- **Project Checkout**: The GitHub repository and primary local working copy contributors use to access and modify the project.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A repository-wide review finds no former-name references in active project identity, code, defaults, or current setup instructions, except references needed to describe the rename itself.
- **SC-002**: A fresh clone uses the renamed GitHub URL and a local directory named `opsgenie-google-calendar-sync`.
- **SC-003**: All installation, setup, and run instructions use `opsgenie-google-calendar-sync` as the project name.

## Assumptions

- The rename includes project documentation, package and executable identity, container naming, GitHub repository identity, and this machine's primary local checkout. Auxiliary worktree paths, branches, contents, and remotes remain unchanged; only pointer repair needed to preserve their connections is in scope.
- GitHub's normal repository rename behavior will preserve access through redirects from the former repository URL.
- The rename does not change synchronization rules, event contents, calendar selection, OAuth scopes, or the user's local installation setup.
- Instructions for migrating the current local installation are out of scope; the user will handle that separately.
- The contributor will review and approve this specification before the implementation plan is created, and review the implementation plan before code or external repository settings are changed.
