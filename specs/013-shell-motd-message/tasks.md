# Tasks: Shell MOTD Message

**Branch**: `013-shell-motd-message` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Foundational Changes

### Configuration Model (FR-002)
- [ ] [T1.1] [P] Write failing test for motd field in ExporterConfigV1Alpha1 in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/config/exporter_test.py`
- [ ] [T1.2] [P] Add optional motd field to ExporterConfigV1Alpha1 in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/config/exporter.py`
- [ ] [T1.3] [P] Verify test T1.1 passes

### Session Metadata (FR-002)
- [ ] [T1.4] [P] Write failing test for motd in session metadata in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/session_test.py`
- [ ] [T1.5] [P] Add motd field to session metadata model in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/session.py`
- [ ] [T1.6] [P] Verify test T1.4 passes
- [ ] [T1.7] [P] Update exporter to include motd from config in session metadata response in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/exporter.py`

## Phase 2: User Story 1 - See exporter info when entering a shell (P1)

### MOTD Display Logic (FR-001, FR-003, FR-004, SC-001)
- [ ] [T2.1] [P1] [US1] Write failing test for MOTD display in launch_shell when no command provided in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- [ ] [T2.2] [P1] [US1] Write failing test for NO MOTD display when command is provided (FR-004) in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- [ ] [T2.3] [P1] [US1] Implement MOTD printing (format per data-model.md) to stdout before subprocess launch in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- [ ] [T2.4] [P1] [US1] Verify tests T2.1 and T2.2 pass

### Display Format (FR-001, SC-001)
- [ ] [T2.5] [P1] [US1] Write failing test for exporter name display format: "Connected to exporter: <name>" in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- [ ] [T2.6] [P1] [US1] Implement exporter name display logic in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- [ ] [T2.7] [P1] [US1] Verify test T2.5 passes

### CLI Integration (SC-001)
- [ ] [T2.8] [P1] [US1] Write failing test for session metadata (including exporter name and motd) passed to launch_shell in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell_test.py`
- [ ] [T2.9] [P1] [US1] Update shell.py to pass session metadata (including motd) to launch_shell in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell.py`
- [ ] [T2.10] [P1] [US1] Verify test T2.8 passes

### Command Execution Verification (FR-004, SC-003)
- [ ] [T2.11] [P1] [US1] Write failing test verifying command output is not polluted when using non-interactive shell in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- [ ] [T2.12] [P1] [US1] Verify test T2.11 passes (no implementation needed if T2.2 properly implemented)

## Phase 3: User Story 2 - Admin configures MOTD content (P2)

### Custom MOTD Text (FR-002, SC-002)
- [ ] [T3.1] [P2] [US2] Write failing test for custom MOTD text display in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- [ ] [T3.2] [P2] [US2] Implement custom MOTD text display logic in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- [ ] [T3.3] [P2] [US2] Verify test T3.1 passes

### Multi-line MOTD (SC-002)
- [ ] [T3.4] [P2] [US2] Write failing test for multi-line MOTD handling in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- [ ] [T3.5] [P2] [US2] Ensure multi-line MOTD display works correctly in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- [ ] [T3.6] [P2] [US2] Verify test T3.4 passes

### Empty/Missing MOTD (SC-002)
- [ ] [T3.7] [P2] [US2] Write failing test for no custom text when motd is None in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- [ ] [T3.8] [P2] [US2] Verify no custom text section shown when motd not configured in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- [ ] [T3.9] [P2] [US2] Verify test T3.7 passes

## Phase 4: Polish & Edge Cases

### Edge Cases
- [ ] [T4.1] [P] Write test for very long MOTD messages (>10000 chars) in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- [ ] [T4.2] [P] Write test for MOTD with special characters (tabs, unicode, ANSI codes) in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- [ ] [T4.3] [P] Verify edge cases handled correctly

### Integration Tests (SC-001, SC-002, SC-003)
- [ ] [T4.4] [P] Add end-to-end test for interactive shell command with MOTD display in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell_e2e_test.py`
- [ ] [T4.5] [P] Add end-to-end test for non-interactive shell (with command) without MOTD in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell_e2e_test.py`

### Documentation
- [ ] [T4.6] [P] Update exporter configuration documentation with motd field example
- [ ] [T4.7] [P] Add example MOTD configurations to user documentation

## Checkpoints

1. **After Phase 1**: Configuration and session metadata models support MOTD field
2. **After Phase 2**: Basic MOTD display works for interactive shells showing exporter name
3. **After Phase 3**: Custom admin-configured MOTD text displays correctly
4. **After Phase 4**: Edge cases handled, integration tests pass, documentation complete

## Dependencies & Execution Order

```
Phase 1 (sequential for proper data flow)
  ├─ T1.1 -> T1.2 -> T1.3
  └─ T1.4 -> T1.5 -> T1.6 -> T1.7
     ↓
Phase 2 (sequential for user story)
  ├─ T2.1, T2.2, T2.11 -> T2.3 -> T2.4, T2.12
  ├─ T2.5 -> T2.6 -> T2.7
  └─ T2.8 -> T2.9 -> T2.10
     ↓
Phase 3 (sequential for user story)
  ├─ T3.1 -> T3.2 -> T3.3
  ├─ T3.4 -> T3.5 -> T3.6
  └─ T3.7 -> T3.8 -> T3.9
     ↓
Phase 4 (parallel within phase)
  ├─ T4.1, T4.2 -> T4.3
  ├─ T4.4, T4.5 (can run in parallel)
  └─ T4.6, T4.7 (can run in parallel)
```

## Implementation Strategy

### TDD Workflow
1. Write a failing test that demonstrates the expected behavior
2. Implement minimal code to make the test pass
3. Verify test passes and refactor if needed
4. Move to next task

### Key Technical Decisions
- **MOTD Display**: Print to stdout in `launch_shell()` before subprocess spawn (interactive mode only)
- **Configuration**: Add optional `motd` field to `ExporterConfigV1Alpha1`
- **Transport**: Include MOTD in session metadata during gRPC session establishment
- **Format**: Simple text format showing exporter name and optional admin message

### Testing Strategy
- Unit tests for configuration model validation
- Unit tests for session metadata handling
- Unit tests for MOTD display logic in `launch_shell()`
- Integration tests for CLI shell command with/without MOTD
- Edge case tests for long messages, special characters, multi-line text

### Files Modified
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/config/exporter.py` - Add motd field to config model
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/session.py` - Add motd field to session metadata
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py` - MOTD display in launch_shell
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/exporter.py` - Transmit motd via session metadata
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell.py` - Pass session metadata to launch_shell

### Test Files Created/Modified
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/config/exporter_test.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/session_test.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell_test.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell_e2e_test.py`
