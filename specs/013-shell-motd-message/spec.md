# Feature Specification: Shell MOTD Message

**Feature Branch**: `013-shell-motd-message`
**Created**: 2026-03-17
**Status**: Draft
**Input**: User description: "Provide a motd message when users get a shell into an exporter - issue #51"

## Clarifications

### Session 2026-03-17

- Q: How does MOTD get from exporter to client? → A: `jmp shell` launches a real shell subprocess (bash/zsh/fish). The MOTD is simply text printed to stdout before the shell process starts. The exporter name is already known client-side. Admin-configured MOTD text can be transmitted as part of the existing session metadata.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See exporter info when entering a shell (Priority: P1)

A user runs `jmp shell -l board=my-board` and upon connecting, sees a welcome message displaying the exporter name before the shell prompt appears. This helps the user understand which device they are connected to, especially when connecting by label selector where the specific exporter assignment is unknown beforehand.

**Why this priority**: Users often connect to devices by label selector and may not know which specific exporter was assigned. The MOTD provides immediate context.

**Independent Test**: Run `jmp shell` against an exporter and verify a welcome message showing the exporter name is printed before the shell prompt.

**Acceptance Scenarios**:

1. **Given** a user connects to an exporter via `jmp shell`, **When** the shell launches, **Then** the exporter name is printed to stdout before the prompt.
2. **Given** an admin has configured a MOTD message for the exporter, **When** a user connects, **Then** the admin-configured message is printed after the exporter name.
3. **Given** no MOTD is configured, **When** a user connects, **Then** only the exporter name line is shown.

---

### User Story 2 - Admin configures MOTD content (Priority: P2)

An administrator configures custom MOTD text in the exporter configuration that is displayed to all users who connect to that exporter.

**Why this priority**: Admins need a mechanism to communicate device-specific instructions, links, or warnings.

**Independent Test**: Add a MOTD field to an exporter config, restart the exporter, connect via shell, and verify the custom message appears.

**Acceptance Scenarios**:

1. **Given** an exporter config with a `motd` field containing custom text, **When** a user connects via `jmp shell`, **Then** the custom text is printed before the shell prompt.
2. **Given** an exporter config without a `motd` field, **When** a user connects, **Then** no custom text section is shown.

---

### Edge Cases

- What happens with very long MOTD messages? Print as-is; no truncation.
- How are multi-line MOTD messages handled? Print each line as-is.
- Should MOTD be shown when running a command (e.g., `jmp shell -- python bar.py`)? No, only for interactive shells.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST print the assigned exporter name to stdout when an interactive shell session starts.
- **FR-002**: The CLI MUST support displaying admin-configured MOTD text from the exporter configuration.
- **FR-003**: The MOTD MUST be printed before the shell subprocess is launched.
- **FR-004**: The MOTD MUST NOT be printed when a command is passed to `jmp shell` (non-interactive usage).

### Key Entities

- **Exporter Config**: May contain an optional `motd` text field.
- **Shell Session**: `launch_shell()` in `utils.py` prints MOTD then spawns the shell subprocess.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users see the exporter name upon entering an interactive shell session.
- **SC-002**: Admin-configured MOTD text appears when set in the exporter config.
- **SC-003**: Non-interactive `jmp shell -- <command>` usage is unaffected.
