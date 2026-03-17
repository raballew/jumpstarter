# Implementation Plan: StorageMux Auto-Detect Compression

**Branch**: `014-storagemux-auto-compression` | **Date**: 2026-03-17 | **Spec**: [spec.md](spec.md)

## Summary

Add compression auto-detection to StorageMux drivers (SDWire, SDMux, DUTLink) based on file extension, matching the existing Flasher driver behavior. Extract the shared detection logic into a common utility.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Click (CLI), jumpstarter driver framework
**Storage**: N/A
**Testing**: pytest
**Target Platform**: Linux
**Project Type**: CLI tool / driver
**Performance Goals**: N/A
**Constraints**: Must match existing Flasher driver behavior exactly
**Scale/Scope**: Common utility + StorageMux driver integration

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Code | Pass | Extract shared logic to avoid duplication |
| II. Minimal Dependencies | Pass | No new deps |
| III. Secure Coding | Pass | No security surface |
| IV. TDD | Pass | Test extension detection logic |
| V. Simplicity | Pass | Reuse existing pattern from Flasher |

## Project Structure

### Source Code (repository root)

```text
python/packages/jumpstarter-driver-flashers/
├── jumpstarter_driver_flashers/
│   ├── compression.py              # NEW: Shared compression detection utility
│   └── driver.py                   # MODIFY: Update to use shared utility
└── tests/
    └── test_compression_detection.py # NEW: Tests for compression detection

python/packages/jumpstarter-driver-sdwire/
├── jumpstarter_driver_sdwire/
│   └── driver.py                   # MODIFY: Add auto-detection using shared utility
└── tests/
    └── test_driver.py              # MODIFY: Add auto-detection tests
```

**Structure Decision**: Extract compression detection to a shared utility in jumpstarter-driver-flashers package, use it in both Flasher and StorageMux drivers.

## Architecture Details

### Shared Compression Detection Utility

**Location**: `python/packages/jumpstarter-driver-flashers/jumpstarter_driver_flashers/compression.py`

**Function Signature**:
```python
def detect_compression_from_url(url: str) -> str | None:
    """
    Detect compression format from URL file extension.

    Args:
        url: File URL or path (may include query parameters and fragments)

    Returns:
        Compression format string ('xz', 'gz', 'bz2', 'zst') or None if uncompressed
    """
```

**Integration Point**: StorageMux driver will call this function before setting compression parameter, only if user hasn't explicitly specified `--compression`.
