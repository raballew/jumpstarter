# Tasks: Fix Lease Filtering

**Input**: Design documents from `/specs/009-fix-lease-filtering/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: No setup needed - this is a bug fix in existing code.

(No tasks)

---

## Phase 2: Foundational

**Purpose**: Understand and verify the existing filtering behavior.

- [ ] T001 Read and understand selector_contains() in python/packages/jumpstarter/jumpstarter/client/selectors.py
- [ ] T002 Read and understand filter_by_selector() in python/packages/jumpstarter/jumpstarter/client/grpc.py

**Checkpoint**: Understanding of current filtering logic complete.

---

## Phase 3: User Story 1 - Filter leases by label selector (Priority: P1)

**Goal**: `jmp get leases -l name=exporter-a` returns only matching leases.

**Independent Test**: Run `jmp get leases -l name=specific-exporter` and verify only matching leases appear.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T003 [US1] Write failing test: filtering with matching label returns only matching leases (validates SC-001) in python/packages/jumpstarter/jumpstarter/client/selectors_test.py
- [ ] T004 [P] [US1] Write failing test: filtering with no matches returns empty list (validates FR-004, SC-003) in python/packages/jumpstarter/jumpstarter/client/selectors_test.py
- [ ] T005 [P] [US1] Write failing test: filtering with subset of compound selector matches (validates FR-002, SC-001) in python/packages/jumpstarter/jumpstarter/client/selectors_test.py

### Implementation for User Story 1

- [ ] T006 [US1] Fix selector_contains() to correctly match user filter against lease selector (implements FR-001, FR-002) in python/packages/jumpstarter/jumpstarter/client/selectors.py
- [ ] T007 [US1] Verify filter_by_selector() correctly uses fixed selector_contains() (implements FR-001) in python/packages/jumpstarter/jumpstarter/client/grpc.py

**Checkpoint**: Label-based filtering works correctly.

---

## Phase 4: User Story 2 - Filter leases by name selector (Priority: P2)

**Goal**: `jmp get leases -l name=my-device` correctly filters by exporter name.

**Independent Test**: Create lease with `name=my-device`, filter with `-l name=my-device`, verify it appears.

### Tests for User Story 2

- [ ] T008 [US2] Write failing test: name selector matches lease targeting that exporter (validates FR-003) in python/packages/jumpstarter/jumpstarter/client/selectors_test.py
- [ ] T009 [P] [US2] Write failing test: name selector does not match lease targeting different exporter (validates FR-003) in python/packages/jumpstarter/jumpstarter/client/selectors_test.py

### Implementation for User Story 2

- [ ] T010 [US2] Ensure name=value selectors are parsed and matched correctly (implements FR-003) in python/packages/jumpstarter/jumpstarter/client/selectors.py

**Checkpoint**: Name-based filtering works correctly.

---

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T011 Handle edge case: invalid selector format in python/packages/jumpstarter/jumpstarter/client/selectors.py
- [ ] T012 Handle edge case: lease with empty selector in python/packages/jumpstarter/jumpstarter/client/selectors.py
- [ ] T013 [P] Write failing test: special characters in label values in python/packages/jumpstarter/jumpstarter/client/selectors_test.py
- [ ] T014 Run full test suite with `make pkg-test-jumpstarter` (verifies SC-002)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: Read-only understanding, no code changes
- **User Story 1 (Phase 3)**: Can start after Phase 2
- **User Story 2 (Phase 4)**: Can start after Phase 3 (shares selectors.py)
- **Polish (Phase 5)**: After all stories complete

### Parallel Opportunities

- T004 and T005 can run in parallel (different test cases)
- T008 and T009 can run in parallel (different test cases)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Understand existing code
2. Complete Phase 3: Fix label filtering (tests first)
3. **STOP and VALIDATE**: Verify filtering works
4. Continue to Phase 4 and 5
