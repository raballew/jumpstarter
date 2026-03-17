# Tasks: Shell MOTD Message

**Branch**: `013-shell-motd-message` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Phase 1: Foundational Changes

### Configuration Model
- [ ] [T1.1] [P] Write failing test for motd field in ExporterConfigV1Alpha1 in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/config/test_exporter.py`
- [ ] [T1.2] [P] Add optional motd field to ExporterConfigV1Alpha1 in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/config/exporter.py`
- [ ] [T1.3] [P] Verify test T1.1 passes

### Session Metadata
- [ ] [T1.4] [P] Write failing test for motd in session metadata in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_session_metadata.py`
- [ ] [T1.5] [P] Add motd field to session metadata model in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/session.py`
- [ ] [T1.6] [P] Verify test T1.4 passes

## Phase 2: User Story 1 - See exporter info when entering a shell (P1)

### MOTD Display Logic
- [ ] [T2.1] Write failing test for MOTD display in launch_shell when no command provided in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_utils.py`
- [ ] [T2.2] Write failing test for NO MOTD display when command is provided in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_utils.py`
- [ ] [T2.3] Implement MOTD printing to stdout before subprocess launch in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- [ ] [T2.4] Verify tests T2.1 and T2.2 pass

### Display Format
- [ ] [T2.5] Write failing test for exporter name display format in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_utils.py`
- [ ] [T2.6] Implement exporter name display logic in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- [ ] [T2.7] Verify test T2.5 passes

### CLI Integration
- [ ] [T2.8] Write failing test for session metadata passed to launch_shell in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/tests/test_shell.py`
- [ ] [T2.9] Update shell.py to pass session metadata (including motd) to launch_shell in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell.py`
- [ ] [T2.10] Verify test T2.8 passes

## Phase 3: User Story 2 - Admin configures MOTD content (P2)

### Custom MOTD Text
- [ ] [T3.1] Write failing test for custom MOTD text display in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_utils.py`
- [ ] [T3.2] Implement custom MOTD text display logic in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- [ ] [T3.3] Verify test T3.1 passes

### Multi-line MOTD
- [ ] [T3.4] Write failing test for multi-line MOTD handling in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_utils.py`
- [ ] [T3.5] Ensure multi-line MOTD display works correctly in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- [ ] [T3.6] Verify test T3.4 passes

### Empty/Missing MOTD
- [ ] [T3.7] Write failing test for no custom text when motd is None in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_utils.py`
- [ ] [T3.8] Verify no custom text section shown when motd not configured in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- [ ] [T3.9] Verify test T3.7 passes

## Phase 4: Polish & Edge Cases

### Edge Cases
- [ ] [T4.1] Write test for very long MOTD messages (>1000 chars) in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_utils.py`
- [ ] [T4.2] Write test for MOTD with special characters (newlines, unicode) in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_utils.py`
- [ ] [T4.3] Verify edge cases handled correctly

### Integration Tests
- [ ] [T4.4] Add end-to-end test for shell command with MOTD display in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/tests/test_shell_e2e.py`
- [ ] [T4.5] Add end-to-end test for non-interactive shell (with command) without MOTD in `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/tests/test_shell_e2e.py`

### Documentation
- [ ] [T4.6] Update exporter configuration documentation with motd field example
- [ ] [T4.7] Add example MOTD configurations to README or user guide

## Checkpoints

1. **After Phase 1**: Configuration and session metadata models support MOTD field
2. **After Phase 2**: Basic MOTD display works for interactive shells showing exporter name
3. **After Phase 3**: Custom admin-configured MOTD text displays correctly
4. **After Phase 4**: Edge cases handled, integration tests pass, documentation complete

## Dependencies & Execution Order

```
Phase 1 (parallel within phase)
  ├─ T1.1 -> T1.2 -> T1.3
  └─ T1.4 -> T1.5 -> T1.6
     ↓
Phase 2 (sequential for user story)
  ├─ T2.1, T2.2 -> T2.3 -> T2.4
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
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/config/exporter.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/session.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell.py`

### Test Files Created/Modified
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/config/test_exporter.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_session_metadata.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/tests/common/test_utils.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/tests/test_shell.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/tests/test_shell_e2e.py`
