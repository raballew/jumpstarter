# Tasks: StorageMux Auto-Detect Compression

**Branch**: `014-storagemux-auto-compression` | **Status**: In Progress

## Phase 1: Foundation

### Setup & Utilities

- [ ] [T001] [P] Create compression detection utility function in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/compression_utils.py
- [ ] [T002] [P] Write failing test for compression detection in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/compression_utils_test.py
- [ ] [T003] Implement compression detection function that maps extensions (.xz, .gz, .bz2, .zst) to Compression enum values
- [ ] [T004] Write failing test for URL query parameter stripping in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/compression_utils_test.py
- [ ] [T005] Implement URL query parameter stripping using urllib.parse.urlparse
- [ ] [T006] Write failing test for double extension handling (.tar.xz) in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/compression_utils_test.py
- [ ] [T007] Implement handling for double extensions (use rightmost compression extension)
- [ ] [T008] Write failing test for case-insensitive extension matching in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/compression_utils_test.py
- [ ] [T009] Implement case-insensitive extension detection

## Phase 2: User Story 1 - Flash compressed images without manual flags (P1)

### StorageMux Auto-Detection

- [ ] [T010] Write failing test for auto-detection in StorageMuxFlasherClient.flash() in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/client_test.py
- [ ] [T011] Update StorageMuxFlasherClient.flash() in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/client.py to auto-detect compression when compression=None
- [ ] [T012] Write failing test for .xz auto-detection in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/client_test.py
- [ ] [T013] Write failing test for .gz auto-detection in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/client_test.py
- [ ] [T014] Write failing test for .bz2 auto-detection in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/client_test.py
- [ ] [T015] Write failing test for .zst auto-detection in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/client_test.py
- [ ] [T016] Write failing test for no compression when path has no compression extension in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/client_test.py
- [ ] [T017] Write failing test for explicit --compression flag override in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/client_test.py
- [ ] [T018] Write failing test for --compression none disabling auto-detection in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/client_test.py

### FlasherClient Refactoring

- [ ] [T019] Write failing test for refactored Flasher driver using shared utility in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-flashers/jumpstarter_driver_flashers/client_test.py
- [ ] [T020] Refactor _get_decompression_command in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-flashers/jumpstarter_driver_flashers/client.py to use shared compression detection utility
- [ ] [T021] Verify existing Flasher tests still pass after refactoring

## Phase 3: User Story 2 - Consistent behavior across driver types (P2)

### Cross-Driver Consistency Tests

- [ ] [T022] Write integration test comparing Flasher and StorageMux behavior with .xz URL in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/integration_test.py
- [ ] [T023] Write integration test comparing Flasher and StorageMux behavior with .gz URL in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/integration_test.py
- [ ] [T024] Write integration test verifying both drivers handle query parameters identically in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/integration_test.py

## Phase 4: Edge Cases & Polish

### Edge Case Handling

- [ ] [T025] Write failing test for URL with query parameters after extension in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/compression_utils_test.py
- [ ] [T026] Write failing test for PosixPath input handling in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/compression_utils_test.py
- [ ] [T027] Update compression detection utility to handle PosixPath input
- [ ] [T028] Write failing test for empty path/URL in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/compression_utils_test.py
- [ ] [T029] Add edge case handling for empty paths

### Documentation & Cleanup

- [ ] [T030] Update StorageMux CLI help text to indicate auto-detection in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter-driver-opendal/jumpstarter_driver_opendal/client.py
- [ ] [T031] Add docstring examples for compression detection utility in /var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/compression_utils.py
- [ ] [T032] Run `make lint-fix` to ensure code style compliance
- [ ] [T033] Run package-specific type checking with `make pkg-ty-jumpstarter` and `make pkg-ty-jumpstarter-driver-opendal`
- [ ] [T034] Verify all tests pass with `make pkg-test-jumpstarter` and `make pkg-test-jumpstarter-driver-opendal`

## Checkpoints

- **CP1**: After T009 - Core compression detection utility complete with all tests passing
- **CP2**: After T018 - StorageMux auto-detection working with all acceptance scenarios covered
- **CP3**: After T021 - Flasher driver refactored to use shared utility without breaking existing functionality
- **CP4**: After T024 - Cross-driver consistency verified through integration tests
- **CP5**: After T034 - All edge cases handled, tests passing, code linted and type-checked

## Dependencies & Execution Order

### Critical Path
1. T001-T009 must complete before any driver integration (provides shared utility)
2. T010-T018 require T001-T009 completion (StorageMux integration depends on utility)
3. T019-T021 require T001-T009 completion (Flasher refactoring depends on utility)
4. T022-T024 require T010-T021 completion (cross-driver tests need both implementations)
5. T025-T034 can be executed after core functionality is complete

### Parallel Opportunities
- T002-T009 (utility tests) can be written in parallel with T001 once function signature is defined
- T012-T018 (StorageMux tests) can be written in parallel
- T019 (Flasher test) can be written in parallel with T010-T018
- T022-T024 (integration tests) can be written in parallel
- T025-T029 (edge case tests) can be written in parallel

## Implementation Strategy

1. **TDD Approach**: Each functional change follows the pattern:
   - Write failing test(s) first
   - Implement minimal code to pass the test
   - Refactor for clarity

2. **Shared Utility First**: Extract compression detection into a common utility to avoid code duplication and ensure consistent behavior

3. **Backward Compatibility**: Explicit --compression flags must override auto-detection to maintain existing behavior

4. **Testing Layers**:
   - Unit tests for compression detection utility
   - Unit tests for driver integration
   - Integration tests for cross-driver consistency
   - Edge case tests for robustness

5. **File Organization**:
   - Shared utility: `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/compression_utils.py`
   - Tests co-located with implementation following `*_test.py` convention
   - Integration tests in driver-opendal package

6. **Extension Mapping**:
   - `.xz` -> `Compression.XZ`
   - `.gz`, `.gzip` -> `Compression.GZIP`
   - `.bz2` -> `Compression.BZ2`
   - `.zst` -> `Compression.ZSTD`
   - No match -> `None` (no compression)
