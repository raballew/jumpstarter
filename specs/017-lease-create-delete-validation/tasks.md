# Tasks: Lease Create/Delete Validation

**Branch**: `017-lease-create-delete-validation`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

---

## Phase 1: Foundational Tasks

### Create Command Validation (Already Complete)
- [x] [T1.1] Validation logic exists in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/create.py` (lines 74-75)
- [x] [T1.2] Test exists in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/create_test.py::test_create_lease_requires_selector_or_name`

---

## Phase 2: Delete Command Error Handling (Priority: P1)

### User Story 2 - Report error when deleting non-existent lease

- [ ] [T2.1] [P1] [Story] Write failing test for deleting UUID that never existed in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/delete_test.py`
  - Test that deleting a UUID that never existed shows "lease <uuid> not found"

- [ ] [T2.2] [P1] [Story] Write failing test for deleting already-deleted lease in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/delete_test.py`
  - Test that deleting an already-deleted lease shows error or warning

- [ ] [T2.3] [P1] [Story] Write failing test for successful delete case in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/delete_test.py`
  - Test that deleting an existing lease shows success message

- [ ] [T2.4] [P1] Create `ResourceNotFoundError` exception in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/exceptions.py`
  - Define new exception class for NOT_FOUND status

- [ ] [T2.5] [P1] Update `translate_grpc_exceptions` in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/grpc.py`
  - Add handling for `StatusCode.NOT_FOUND` to raise `ResourceNotFoundError`
  - Keep existing exception handling for UNAVAILABLE and UNKNOWN

- [ ] [T2.6] [P1] Update `delete_lease` in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/config/client.py`
  - Catch `ResourceNotFoundError` and return/raise appropriately for CLI to handle

- [ ] [T2.7] [P1] [Story] Update `delete_leases` in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/delete.py`
  - Wrap `config.delete_lease(name=name)` in try/except to catch `ResourceNotFoundError`
  - For single delete: Display error message "lease <uuid> not found" and exit with error code
  - For `--all` or `--selector`: Log warning but continue with remaining deletes

- [ ] [T2.8] [P1] Verify all tests pass for delete validation

---

## Phase 3: Edge Cases and Polish (Priority: P2)

- [ ] [T3.1] [P2] [Story] Write test for `--all` flag with some already-deleted leases in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/delete_test.py`
  - Verify warnings are shown but other deletes continue

- [ ] [T3.2] [P2] [Story] Write test for `--selector` with mixed valid/invalid leases in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/delete_test.py`
  - Verify warnings are shown but other deletes continue

- [ ] [T3.3] [P2] Manual integration test: Create and delete lease workflow
  - Run `jmp create lease -l foo=bar --duration 1h`
  - Run `jmp delete leases <uuid>` - verify success
  - Run `jmp delete leases <uuid>` again - verify error message
  - Run `jmp delete leases <fake-uuid>` - verify error message

- [ ] [T3.4] [P2] Update documentation if needed (only if error message format changes significantly)

---

## Checkpoints

**After Phase 2**:
- All delete validation tests pass
- Deleting non-existent leases shows clear error
- `--all` and `--selector` handle not-found gracefully

**After Phase 3**:
- Edge cases tested and working
- Manual integration tests pass
- Feature complete per spec.md

---

## Dependencies & Execution Order

1. **T2.1, T2.2, T2.3** can run in parallel (all are test creation)
2. **T2.4** must complete before T2.5 (exception class before grpc handler)
3. **T2.5** must complete before T2.6 (grpc exception handling before config method)
4. **T2.6** must complete before T2.7 (config method before CLI)
5. **T2.8** depends on T2.1, T2.2, T2.3, T2.7 (runs all tests)
6. **Phase 3** depends on Phase 2 completion

---

## Implementation Strategy

### TDD Approach
Following the project's TDD requirement:
1. Write failing tests first (T2.1, T2.2, T2.3)
2. Implement minimal code to pass tests (T2.4, T2.5, T2.6, T2.7)
3. Refactor and clean up (included in each task)
4. Add edge case tests (T3.1, T3.2)

### Error Handling Strategy
- Add new exception type `ResourceNotFoundError` for NOT_FOUND gRPC status
- Update `translate_grpc_exceptions` to handle this status code
- CLI layer catches and formats user-friendly error messages
- Bulk operations (--all, --selector) show warnings but continue

### File Modifications
All file paths are absolute and tested:
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/exceptions.py` - New exception type
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/grpc.py` - Exception translation
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/config/client.py` - Delete method
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/delete.py` - CLI command
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/delete_test.py` - New test file
