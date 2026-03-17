# Feature Specification: Fix Lease Filtering

**Feature Branch**: `009-fix-lease-filtering`
**Created**: 2026-03-17
**Status**: Draft
**Input**: User description: "Fix lease filtering - issue #29"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Filter leases by label selector (Priority: P1)

A user runs `jmp get leases -l name=my-exporter` and expects only leases whose selector matches `name=my-exporter` to appear. Currently, unrelated leases are also returned because the server-side API only filters by matchLabels, and the client-side `filter_by_selector` does not properly match the user's query against the lease's stored selector.

**Why this priority**: This is the core bug. Users cannot trust lease filtering output, making it useless for multi-tenant or busy environments.

**Independent Test**: Run `jmp get leases -l name=specific-exporter` and verify only leases targeting that exporter appear.

**Acceptance Scenarios**:

1. **Given** multiple leases with different selectors exist, **When** user runs `jmp get leases -l name=exporter-a`, **Then** only leases with selector `name=exporter-a` are shown.
2. **Given** no leases match the provided selector, **When** user runs `jmp get leases -l name=nonexistent`, **Then** an empty list is returned.
3. **Given** leases with compound selectors (e.g., `board=arm,region=us`), **When** user filters by a subset (`-l board=arm`), **Then** leases containing that label in their selector are shown.

---

### User Story 2 - Filter leases by name selector (Priority: P2)

A user filters leases using a `name=<exporter-name>` selector. The server returns all leases, and the client must correctly identify leases whose selector references that specific exporter name.

**Why this priority**: Name-based targeting is a common pattern when users know the specific exporter they want.

**Independent Test**: Create a lease targeting `name=my-device`, then filter with `-l name=my-device` and verify it appears.

**Acceptance Scenarios**:

1. **Given** a lease created with `name=my-device` selector, **When** user runs `jmp get leases -l name=my-device`, **Then** that lease appears in results.
2. **Given** a lease created with `name=other-device` selector, **When** user runs `jmp get leases -l name=my-device`, **Then** that lease does not appear.

---

### Edge Cases

- What happens when the user provides an invalid label selector format (e.g., `-l ===invalid`)?
- What happens when a lease has an empty selector?
- How does filtering behave with special characters in label values?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST filter leases client-side so that only leases whose selector matches the user-provided `-l` filter are displayed.
- **FR-002**: Label matching MUST compare key-value pairs: a lease matches if its selector contains all key-value pairs specified in the filter.
- **FR-003**: Name-based selectors (`name=<value>`) MUST be matched against the lease's selector matchLabels.
- **FR-004**: When no leases match the filter, the CLI MUST display an empty result set (not an error).

### Key Entities

- **Lease**: Has a selector with matchLabels (key-value pairs). The selector defines which exporter the lease targets.
- **Label Selector**: A comma-separated list of key=value pairs used to filter leases.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Filtering by label selector returns only matching leases with 100% accuracy (no false positives).
- **SC-002**: All existing unit tests for lease operations continue to pass.
- **SC-003**: Filtering with no matches returns an empty list, not an error.
