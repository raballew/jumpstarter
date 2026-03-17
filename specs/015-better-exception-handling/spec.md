# Feature Specification: Better Exception Handling

**Feature Branch**: `015-better-exception-handling`
**Created**: 2026-03-17
**Status**: Draft
**Input**: User description: "Better exception handling for CLI - issue #57"

## Clarifications

### Session 2026-03-17

- Q: Relationship with issue #175 (branch 016, cert error stack trace)? → A: This issue supersedes #175. TLS certificate errors are handled here as one of the common exceptions. Issue #175 should be closed as covered.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See friendly error messages instead of stack traces (Priority: P1)

A user encounters a common error (network timeout, connection refused, TLS failure) and sees a full Python stack trace. Instead, the CLI should display a concise, actionable error message that helps the user understand what went wrong and how to fix it.

**Why this priority**: Stack traces are intimidating and unhelpful for end users. This is the most visible UX problem.

**Independent Test**: Simulate a connection timeout and verify the CLI shows a one-line error message instead of a traceback.

**Acceptance Scenarios**:

1. **Given** the server is unreachable, **When** user runs any jmp command, **Then** a message like "Error: Could not connect to server. Check that the endpoint is correct and reachable." is shown.
2. **Given** a TLS certificate error occurs, **When** user runs `jmp login`, **Then** a message like "Error: TLS certificate verification failed for <host>. Use --insecure to skip verification." is shown (covers issue #175).
3. **Given** the user's authentication token has expired, **When** user runs a command, **Then** a message like "Error: Authentication failed. Run 'jmp login' to re-authenticate." is shown.

---

### User Story 2 - Retain debug output for troubleshooting (Priority: P2)

When a user or developer needs full error details, they can enable verbose/debug output to see the complete stack trace.

**Why this priority**: Developers and support teams need full tracebacks for debugging.

**Independent Test**: Run a command that fails with `--debug` or equivalent flag and verify the full stack trace is shown.

**Acceptance Scenarios**:

1. **Given** any error occurs, **When** user runs the command with a debug flag, **Then** the full stack trace is displayed along with the friendly message.

---

### Edge Cases

- What happens with unexpected/unknown exceptions? Show a generic message with the exception type and suggest reporting the issue.
- How are multiple chained exceptions displayed? Show only the root cause in the friendly message.
- Should the friendly message be written to stderr while the traceback goes to a log file? Friendly message to stderr, traceback only with debug flag.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST catch common exceptions and display user-friendly one-line error messages.
- **FR-002**: Common exceptions MUST include: connection errors, TLS/SSL errors (including ClientConnectorCertificateError and SSLCertVerificationError), authentication errors, timeout errors, and permission errors.
- **FR-003**: Each friendly error message MUST include a suggested action when possible.
- **FR-004**: A mechanism MUST exist to show full stack traces for debugging purposes.
- **FR-005**: Unexpected exceptions MUST show a generic friendly message with instructions to report the issue, plus the exception type.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The 5 most common error scenarios show friendly messages instead of stack traces.
- **SC-002**: Full stack traces are available via a debug mechanism.
- **SC-003**: No user-facing command produces a raw Python traceback under normal operation.
- **SC-004**: This change also satisfies the requirements of issue #175 (cert error stack trace).
