# Tasks: StorageMux Auto-Detect Compression

**Feature**: 014-storagemux-auto-compression | **Status**: Not Started

## Phase 0: Setup & Research

- [ ] [T001] Research: Locate Flasher driver compression detection logic in python/packages/jumpstarter-driver-flashers/
- [ ] [T002] Research: Identify StorageMux driver files that need modification in python/packages/jumpstarter-driver-sdwire/
- [ ] [T003] Research: Determine optimal location for shared compression detection utility

## Phase 1: Shared Compression Detection Utility (Story: User Story 1)

- [ ] [T004] [P1] [Story] Test: Write failing test for detect_compression_from_url() with .xz extension in python/packages/jumpstarter-driver-flashers/tests/test_compression_detection.py
- [ ] [T005] [P1] [Story] Implement: Create detect_compression_from_url() function that passes .xz test in python/packages/jumpstarter-driver-flashers/jumpstarter_driver_flashers/compression.py
- [ ] [T006] [P1] [Story] Test: Write failing test for .gz extension detection
- [ ] [T007] [P1] [Story] Implement: Extend detect_compression_from_url() to handle .gz extension
- [ ] [T008] [P1] [Story] Test: Write failing test for .bz2 extension detection
- [ ] [T009] [P1] [Story] Implement: Extend detect_compression_from_url() to handle .bz2 extension
- [ ] [T010] [P1] [Story] Test: Write failing test for .zst extension detection
- [ ] [T011] [P1] [Story] Implement: Extend detect_compression_from_url() to handle .zst extension
- [ ] [T012] [P1] [Story] Test: Write failing test for uncompressed files (no compression extension)
- [ ] [T013] [P1] [Story] Implement: Handle uncompressed files by returning None

## Phase 2: URL Query Parameter Handling (Story: User Story 1)

- [ ] [T014] [P1] [Story] Test: Write failing test for URL with query parameters (image.raw.xz?token=abc)
- [ ] [T015] [P1] [Story] Implement: Strip query parameters using urllib.parse.urlparse before extension detection
- [ ] [T016] [P1] [Story] Test: Write failing test for URL with fragment identifier (image.raw.gz#section)
- [ ] [T017] [P1] [Story] Implement: Strip fragment identifiers before extension detection
- [ ] [T018] [P1] [Story] Test: Write failing test for double extensions (.tar.xz should detect .xz)
- [ ] [T019] [P1] [Story] Implement: Extract only the final extension for compression detection

## Phase 3: Case-Insensitive Extension Matching

- [ ] [T020] [P1] Test: Write failing test for uppercase extensions (.XZ, .GZ)
- [ ] [T021] [P1] Implement: Convert extensions to lowercase before matching

## Phase 4: Integrate with StorageMux Driver (Story: User Story 1)

- [ ] [T022] [P1] [Story] Test: Write failing test for auto-detection in SDWire driver flash command
- [ ] [T023] [P1] [Story] Implement: Import and use detect_compression_from_url() in python/packages/jumpstarter-driver-sdwire/jumpstarter_driver_sdwire/driver.py
- [ ] [T024] [P1] [Story] Test: Write failing test that explicit --compression flag overrides auto-detection
- [ ] [T025] [P1] [Story] Implement: Check if --compression is explicitly set; if yes, skip auto-detection
- [ ] [T026] [P1] [Story] Test: Write failing test for --compression none overriding auto-detection
- [ ] [T027] [P1] [Story] Implement: Handle --compression none explicitly to skip auto-detection

## Phase 5: Consistency Across Drivers (Story: User Story 2)

- [ ] [T028] [P2] [Story] Test: Write comparative test for Flasher and StorageMux with same compressed URL
- [ ] [T029] [P2] [Story] Refactor: Update Flasher driver to use shared detect_compression_from_url() function
- [ ] [T030] [P2] [Story] Test: Verify both drivers produce identical behavior

## Phase 6: Edge Cases & Error Handling

- [ ] [T031] [P1] Test: Write failing test for unrecognized compression extension (.rar, .zip)
- [ ] [T032] [P1] Implement: Return None for unrecognized extensions
- [ ] [T033] [P1] Test: Write failing test for malformed URLs
- [ ] [T034] [P1] Implement: Handle URL parsing errors gracefully

## Phase 7: Documentation & Integration

- [ ] [T035] [P2] Docs: Update driver documentation to mention auto-detection behavior
- [ ] [T036] [P2] Docs: Add examples of compressed image flashing without --compression flag
- [ ] [T037] [P2] Integration: Run full test suite (make pkg-test-jumpstarter-driver-sdwire)
- [ ] [T038] [P2] Integration: Run type checking (make pkg-ty-jumpstarter-driver-sdwire)
- [ ] [T039] [P2] Integration: Run linting (make lint-fix)

## Acceptance Criteria Verification

- [ ] [T040] [P1] [Story] E2E Test: Verify acceptance scenario 1 - .raw.xz auto-detection
- [ ] [T041] [P1] [Story] E2E Test: Verify acceptance scenario 2 - .raw.gz auto-detection
- [ ] [T042] [P1] [Story] E2E Test: Verify acceptance scenario 3 - .raw no decompression
- [ ] [T043] [P1] [Story] E2E Test: Verify acceptance scenario 4 - --compression none override
- [ ] [T044] [P2] [Story] E2E Test: Verify User Story 2 - consistent behavior across drivers
