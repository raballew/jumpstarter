# Tasks: Improve Lease Output Usability

**Branch**: `012-lease-output-usability`
**Spec**: [spec.md](spec.md)
**Plan**: [plan.md](plan.md)

## Task List

### Phase 1: Setup & Foundation

- [ ] [T001] [P] Setup: Write failing test for default columns in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/test_leases.py
- [ ] [T002] [P] Setup: Write failing test for wide output mode in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/test_leases.py
- [ ] [T003] [P] Setup: Write failing test for remaining time calculation in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/test_datetime.py

### Phase 2: Time Utilities (Foundation)

- [ ] [T004] [P] Foundation: Implement time_remaining function in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/datetime.py
- [ ] [T005] [P] Foundation: Verify time_remaining tests pass for various states (active >1h, <1h, <1m, expired, pending)

### Phase 3: User Story 1 - Default Columns (P1)

- [ ] [T006] [S1] Add output_mode parameter support to rich_add_columns in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/leases.py
- [ ] [T007] [S1] Add output_mode parameter support to rich_add_rows in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/leases.py
- [ ] [T008] [S1] Implement default column set (NAME, CLIENT, EXPORTER, REMAINING) in rich_add_columns
- [ ] [T009] [S1] Implement wide column set (all existing columns) in rich_add_columns
- [ ] [T010] [S1] Update rich_add_rows to output appropriate columns based on output_mode
- [ ] [T011] [S1] Verify default columns test passes

### Phase 4: User Story 2 - Relative Time Display (P2)

- [ ] [T012] [S2] Add REMAINING column calculation using time_remaining in rich_add_rows
- [ ] [T013] [S2] Handle expired lease display ("Expired") in REMAINING column
- [ ] [T014] [S2] Handle pending lease display ("-") in REMAINING column
- [ ] [T015] [S2] Verify remaining time test passes

### Phase 5: CLI Integration

- [ ] [T016] Add --output wide option to opt_output_all in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/opt.py
- [ ] [T017] Update model_print to pass output_mode to rich_add_columns in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/print.py
- [ ] [T018] Update model_print to pass output_mode to rich_add_rows in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/print.py
- [ ] [T019] Verify get leases command shows default columns by default
- [ ] [T020] Verify get leases -o wide shows all columns

### Phase 6: Edge Cases & Polish

- [ ] [T021] [P] Write test for lease with no begin_time (pending state)
- [ ] [T022] [P] Write test for lease with <1 minute remaining
- [ ] [T023] [P] Handle edge case: lease with no begin_time displays "-" in REMAINING
- [ ] [T024] [P] Handle edge case: lease with <1 minute remaining displays "<1m"
- [ ] [T025] [P] Verify JSON/YAML output modes are not affected by changes
- [ ] [T026] [P] Verify NAME output mode is not affected by changes
- [ ] [T027] Run full test suite: make pkg-test-jumpstarter-kubernetes
- [ ] [T028] Run full test suite: make pkg-test-jumpstarter-cli-common
- [ ] [T029] Run linting: make lint-fix
- [ ] [T030] Run type checking: make pkg-ty-jumpstarter-kubernetes

## Checkpoints

### CP1: Foundation Complete (After T005)
- time_remaining function implemented and tested
- All time calculation states handled correctly

### CP2: User Story 1 Complete (After T011)
- Default columns (NAME, CLIENT, EXPORTER, REMAINING) working
- Wide output mode showing all columns
- Tests passing for column selection

### CP3: User Story 2 Complete (After T015)
- REMAINING column showing relative time
- Expired and pending states handled
- Tests passing for time display

### CP4: CLI Integration Complete (After T020)
- CLI supports -o wide flag
- Default output shows 4 columns
- Wide output shows all columns

### CP5: Ready for Review (After T030)
- All edge cases handled
- Full test suite passing
- Code linted and type-checked

## Dependencies & Execution Order

### Critical Path
T001-T003 (tests) -> T004-T005 (foundation) -> T006-T011 (S1) -> T012-T015 (S2) -> T016-T020 (CLI) -> T021-T030 (polish)

### Parallel Work Opportunities
- T001, T002, T003 can be written in parallel [P]
- T021, T022 can be written in parallel [P]
- T027, T028, T030 can run in parallel [P]

### Sequential Dependencies
1. Tests must be written before implementation (TDD)
2. Foundation (time_remaining) must exist before REMAINING column can be implemented
3. Output mode parameter support must be added before column selection logic
4. CLI integration depends on model layer changes being complete

## Implementation Strategy

### TDD Approach
1. Write failing tests first for each user story (T001-T003, T021-T022)
2. Implement minimal code to pass tests
3. Refactor for clarity and maintainability
4. Verify tests still pass

### Output Mode Design
- Default (no -o flag): 4 columns (NAME, CLIENT, EXPORTER, REMAINING)
- Wide (-o wide): All columns (NAME, CLIENT, SELECTOR, EXPORTER, DURATION, STATUS, REASON, BEGIN, END, AGE)
- JSON/YAML/NAME modes: Unaffected (no table rendering)

### Time Formatting Rules
| Remaining Time | Display |
|---------------|---------|
| > 1 hour | "Xh Ym" (e.g., "2h 15m") |
| > 1 minute, < 1 hour | "Xm" (e.g., "45m") |
| < 1 minute | "<1m" |
| Expired (negative) | "Expired" |
| Pending (no begin_time) | "-" |
| No duration set | "-" |

### Testing Strategy
1. Unit tests for time_remaining function (all states)
2. Unit tests for rich_add_columns (default vs wide)
3. Unit tests for rich_add_rows (column data)
4. Integration tests for model_print with different output modes
5. Edge case tests for pending and expired leases

### File Modification Summary
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/datetime.py` - Add time_remaining function
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/leases.py` - Add output_mode support, REMAINING column
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/test_leases.py` - Add column and time display tests
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/test_datetime.py` - Add time_remaining tests (create if needed)
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/opt.py` - Add "wide" to OutputMode
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli-common/jumpstarter_cli_common/print.py` - Pass output_mode to rich methods

### Success Metrics (from spec.md)
- SC-001: Default `jmp get leases` output shows only 4 most relevant columns
- SC-002: Users can determine lease remaining time at a glance without calculation
- SC-003: Wide output mode shows all columns for users who need full details
