# Tasks: Better Exception Handling

**Branch**: `015-better-exception-handling` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Setup & Foundation

### Setup
- [ ] [T001] Read project structure rules at `/var/home/raballew/code/jumpstarter/.claude/rules/project-structure.md`
- [ ] [T002] Review existing exception handling in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T003] Review CLI entry point at `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/jmp.py`

### Foundational
- [ ] [T004] [P] Write failing test for exception-to-message mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T005] [P] Write failing test for debug mode preserving stack traces in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`

## Phase 2: User Story 1 - Friendly Error Messages (P1)

### Exception Mapping Infrastructure
- [ ] [T006] [S1] Add exception-to-message mapping function in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T007] [S1] Implement message formatter with suggested actions in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`

### TLS/SSL Error Handling
- [ ] [T008] [S1] Write failing test for ClientConnectorCertificateError handling in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T009] [S1] Add ClientConnectorCertificateError mapping (aiohttp) in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T010] [S1] Write failing test for SSLCertVerificationError handling in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T011] [S1] Add SSLCertVerificationError mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`

### Connection Error Handling
- [ ] [T012] [S1] Write failing test for ConnectionRefusedError handling in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T013] [S1] Add ConnectionRefusedError mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T014] [S1] Write failing test for TimeoutError handling in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T015] [S1] Add TimeoutError and asyncio.TimeoutError mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`

### Authentication Error Handling
- [ ] [T016] [S1] Write failing test for gRPC UNAUTHENTICATED status handling in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T017] [S1] Add grpclib.StatusCode.UNAUTHENTICATED mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T018] [S1] Write failing test for gRPC PERMISSION_DENIED status handling in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T019] [S1] Add grpclib.StatusCode.PERMISSION_DENIED mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`

### Configuration Error Handling
- [ ] [T020] [S1] Write failing test for config FileNotFoundError handling in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T021] [S1] Add config FileNotFoundError mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`

### Unknown Exception Handling
- [ ] [T022] [S1] Write failing test for unknown exception fallback message in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T023] [S1] Add generic fallback handler for unexpected exceptions in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`

### Integration
- [ ] [T024] [S1] Update async_handle_exceptions decorator to use new mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T025] [S1] Update handle_exceptions decorator to use new mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T026] [S1] Update handle_exceptions_with_reauthentication to use new mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`

## Phase 3: User Story 2 - Debug Output (P2)

### Debug Mode Implementation
- [ ] [T027] [S2] Write failing test for --log-level DEBUG showing full tracebacks in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T028] [S2] Add check for DEBUG log level in exception handlers in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T029] [S2] Write failing test for JUMPSTARTER_DEBUG env var showing full tracebacks in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T030] [S2] Add check for JUMPSTARTER_DEBUG environment variable in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T031] [S2] Ensure debug mode shows both friendly message and full stack trace in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`

## Phase 4: Polish & Edge Cases

### Edge Case Handling
- [ ] [T032] [P] Write failing test for chained exceptions in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T033] [P] Ensure chained exceptions display appropriately in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T034] [P] Write failing test for exceptions within BaseExceptionGroup in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions_test.py`
- [ ] [T035] [P] Ensure BaseExceptionGroup handling works with new mapping in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`

### Testing & Validation
- [ ] [T036] [P] Run package tests with `make pkg-test-jumpstarter-cli-common`
- [ ] [T037] [P] Run type checking with `make pkg-ty-jumpstarter-cli-common`
- [ ] [T038] [P] Run linting with `make lint-fix`
- [ ] [T039] [P] Manually test all common error scenarios from research.md
- [ ] [T040] [P] Verify no raw stack traces appear in normal operation
- [ ] [T041] [P] Verify debug mode shows full tracebacks

### Documentation
- [ ] [T042] [P] Add docstrings to new functions in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/exceptions.py`
- [ ] [T043] [P] Update CLAUDE.md if needed at `/var/home/raballew/code/jumpstarter/CLAUDE.md`

---

## Checkpoints

- **CP1** (After T005): Foundation tests written and failing
- **CP2** (After T026): All friendly error messages implemented for User Story 1
- **CP3** (After T031): Debug mode fully functional for User Story 2
- **CP4** (After T041): All tests passing, edge cases handled, ready for review

---

## Dependencies & Execution Order

### Sequential Dependencies
1. T001-T003 must complete before other tasks (understanding existing code)
2. T004-T005 must complete before T006 (tests guide implementation)
3. T006-T007 must complete before T008-T023 (mapping infrastructure needed)
4. T024-T026 must complete before T027 (integration before debug mode)
5. T027-T031 must complete before T032 (debug mode before edge cases)
6. T036-T038 can run in parallel after all implementation tasks complete
7. T042-T043 should be done last

### Parallel Opportunities
- T008-T023: Individual exception type tests and implementations can be done in parallel
- T036-T038: All validation tasks can run in parallel
- T039-T041: Manual testing tasks can run in parallel

---

## Implementation Strategy

### TDD Approach
1. For each exception type, write the failing test first (T008, T010, T012, etc.)
2. Implement minimal code to pass the test (T009, T011, T013, etc.)
3. Refactor if needed while keeping tests green

### Testing Strategy
- Unit tests for each exception-to-message mapping
- Unit tests for debug mode behavior
- Integration tests using existing CLI commands
- Manual verification of common error scenarios

### Risk Mitigation
- Preserve existing exception handling behavior
- Ensure debug mode doesn't break existing workflows
- Maintain compatibility with BaseExceptionGroup handling
- Don't change exit codes

### Success Metrics
- All tests in exceptions_test.py pass
- No raw Python tracebacks in normal operation
- Full tracebacks available with --log-level DEBUG
- All common error scenarios from research.md display friendly messages
