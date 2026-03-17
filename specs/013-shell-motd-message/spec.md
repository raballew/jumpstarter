# Feature Specification: Shell MOTD Message

**Feature Branch**: `013-shell-motd-message`
**Created**: 2026-03-17
**Status**: Draft
**Input**: User description: "Provide a motd message when users get a shell into an exporter - issue #51"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See exporter info when entering a shell (Priority: P1)

A user runs `jmp shell -l board=my-board` and upon connecting, sees a welcome message displaying the exporter name and any admin-configured information. This helps the user understand which device they are connected to and how to interact with it.

**Why this priority**: Users often connect to devices by label selector and may not know which specific exporter was assigned. The MOTD provides immediate context.

**Independent Test**: Run `jmp shell` against an exporter and verify a welcome message showing the exporter name is displayed before the prompt.

**Acceptance Scenarios**:

1. **Given** a user connects to an exporter via `jmp shell`, **When** the connection is established, **Then** the exporter name is displayed.
2. **Given** an admin has configured a MOTD message for the exporter, **When** a user connects, **Then** the admin-configured message is shown.
3. **Given** no MOTD is configured, **When** a user connects, **Then** only the basic exporter name and connection info are shown.

---

### User Story 2 - Admin configures MOTD content (Priority: P2)

An administrator configures custom MOTD text in the exporter configuration that is displayed to all users who connect to that exporter.

**Why this priority**: Admins need a mechanism to communicate device-specific instructions, links, or warnings.

**Independent Test**: Add a MOTD field to an exporter config, restart the exporter, connect via shell, and verify the custom message appears.

**Acceptance Scenarios**:

1. **Given** an exporter config with a `motd` field containing custom text, **When** a user connects via `jmp shell`, **Then** the custom text is displayed.
2. **Given** an exporter config without a `motd` field, **When** a user connects, **Then** no custom text section is shown.

---

### Edge Cases

- What happens with very long MOTD messages?
- How are multi-line MOTD messages handled?
- Should MOTD be shown when connecting via `jmp shell` with an existing lease vs creating a new one?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST display the assigned exporter name when a shell session starts.
- **FR-002**: The CLI MUST support displaying admin-configured MOTD text from the exporter configuration.
- **FR-003**: The MOTD MUST be displayed before the user's first command prompt.
- **FR-004**: The MOTD display MUST NOT interfere with scripted or non-interactive usage.

### Key Entities

- **Exporter Config**: May contain an optional `motd` text field.
- **Shell Session**: Connects to an exporter and displays the MOTD before yielding control.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users see the exporter name upon entering a shell session.
- **SC-002**: Admin-configured MOTD text appears when set in the exporter config.
- **SC-003**: Shell sessions without MOTD configuration work identically to current behavior.
