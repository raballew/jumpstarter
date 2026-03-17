# Feature Specification: Lease Create/Delete Validation

**Feature Branch**: `017-lease-create-delete-validation`
**Created**: 2026-03-17
**Status**: Draft
**Input**: User description: "jmp create allows invalid leases, jmp delete allows deleting already-deleted leases - issue #250"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Prevent creating leases without a selector (Priority: P1)

A user runs `jmp create lease --duration 2h` without providing a selector. Currently, this creates an unsatisfiable lease that can never be fulfilled. The CLI should validate that a selector is provided and show a clear error, matching the behavior of `jmp shell`.

**Why this priority**: Creating invalid leases wastes resources and confuses users who expect them to work.

**Independent Test**: Run `jmp create lease --duration 2h` without a selector and verify an error is returned.

**Acceptance Scenarios**:

1. **Given** no selector is provided, **When** user runs `jmp create lease --duration 2h`, **Then** an error message "Error: A selector is required to create a lease" is shown and no lease is created.
2. **Given** a valid selector is provided, **When** user runs `jmp create lease -l board=arm --duration 2h`, **Then** the lease is created normally.

---

### User Story 2 - Report error when deleting non-existent lease (Priority: P2)

A user runs `jmp delete leases <uuid>` for a lease that has already been deleted. Currently, the command reports success every time. It should indicate that the lease was not found or already deleted.

**Why this priority**: Silent false-success on delete operations makes it impossible to verify whether an operation actually did something.

**Independent Test**: Delete a lease, then delete it again and verify the second attempt shows an error or warning.

**Acceptance Scenarios**:

1. **Given** a lease exists, **When** user runs `jmp delete leases <uuid>`, **Then** the lease is deleted and a success message is shown.
2. **Given** a lease has already been deleted, **When** user runs `jmp delete leases <uuid>` again, **Then** an error or warning like "lease <uuid> not found" is shown.
3. **Given** a UUID that never existed, **When** user runs `jmp delete leases <uuid>`, **Then** an error "lease <uuid> not found" is shown.

---

### Edge Cases

- What if the server returns a 404 for a deleted lease but the CLI ignores the error code?
- Should `jmp delete leases` with `--all` skip already-deleted leases silently?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `jmp create lease` MUST require a selector and reject requests without one.
- **FR-002**: The error message for missing selector MUST match the style used by `jmp shell`.
- **FR-003**: `jmp delete leases` MUST report when a lease is not found or already deleted.
- **FR-004**: Bulk delete operations (`--all`) MAY skip not-found leases with a warning rather than an error.

### Key Entities

- **Lease**: Requires a selector to be valid. Has a lifecycle state that determines if it can be deleted.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Creating a lease without a selector produces a clear error and no lease is created.
- **SC-002**: Deleting an already-deleted lease produces a not-found error or warning.
- **SC-003**: Valid create and delete operations continue to work unchanged.
