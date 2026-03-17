# Feature Specification: Improve Lease Output Usability

**Feature Branch**: `012-lease-output-usability`
**Created**: 2026-03-17
**Status**: Draft
**Input**: User description: "Improve jmp get leases usability - issue #45"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See relevant lease information at a glance (Priority: P1)

A user runs `jmp get leases` and wants to quickly understand which exporters are leased, by whom, and when the lease expires. The current default columns include SELECTOR and DURATION which are less useful than CLIENT, EXPORTER, and EXPIRATION for daily operations.

**Why this priority**: The default output is the most common interaction point. Showing the most relevant columns by default reduces cognitive load.

**Independent Test**: Run `jmp get leases` and verify the default columns are NAME, CLIENT, EXPORTER, and EXPIRATION (relative time).

**Acceptance Scenarios**:

1. **Given** active leases exist, **When** user runs `jmp get leases`, **Then** the default columns shown are NAME, CLIENT, EXPORTER, and EXPIRATION.
2. **Given** the user wants to see all columns, **When** user runs `jmp get leases -o wide`, **Then** all columns including SELECTOR, DURATION, STATUS, BEGIN, END, AGE are shown.

---

### User Story 2 - See expiration as relative time (Priority: P2)

The EXPIRATION column should display time remaining in a human-friendly format like "2h 15m" or "45m" rather than an absolute timestamp.

**Why this priority**: Relative time is immediately actionable without timezone mental conversion.

**Independent Test**: Run `jmp get leases` with an active lease and verify the EXPIRATION column shows relative time.

**Acceptance Scenarios**:

1. **Given** a lease expiring in 2 hours and 15 minutes, **When** user runs `jmp get leases`, **Then** the EXPIRATION column shows "2h 15m" or similar.
2. **Given** an expired lease shown with `--all`, **When** user views it, **Then** the EXPIRATION column shows "Expired" or similar.

---

### Edge Cases

- What happens when a lease has no begin time (not yet started)?
- How is the expiration displayed when less than 1 minute remains?
- What if the output is piped (non-TTY) -- should absolute time be shown instead?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The default columns for `jmp get leases` MUST be NAME, CLIENT, EXPORTER, and EXPIRATION.
- **FR-002**: The EXPIRATION column MUST show remaining time in human-readable relative format.
- **FR-003**: A wide output mode (`-o wide`) MUST show all available columns.
- **FR-004**: Expired leases MUST clearly indicate they have expired.

### Key Entities

- **Lease**: Has name, client, exporter, selector, duration, begin_time, end_time, status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Default `jmp get leases` output shows only the 4 most relevant columns.
- **SC-002**: Users can determine lease expiration at a glance without calculation.
- **SC-003**: Wide output mode shows all columns for users who need full details.
