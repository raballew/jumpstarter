# Implementation Plan: Improve Lease Output Usability

**Branch**: `012-lease-output-usability` | **Date**: 2026-03-17 | **Spec**: [spec.md](spec.md)

## Summary

Change `jmp get leases` default columns to NAME, CLIENT, EXPORTER, REMAINING and add a REMAINING column showing relative time until lease expiration. Support `-o wide` for all columns. This also satisfies issue #32.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Click, Rich (table rendering), pydantic
**Storage**: N/A
**Testing**: pytest
**Target Platform**: Linux, macOS
**Project Type**: CLI tool
**Performance Goals**: N/A
**Constraints**: Must not break `-o json`/`-o yaml`/`-o name` output modes
**Scale/Scope**: Changes in `jumpstarter-kubernetes` (lease model and time utilities) and `jumpstarter-cli-common` (output formatting)

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Code | Pass | Clear column restructuring |
| II. Minimal Dependencies | Pass | Uses existing Rich library |
| III. Secure Coding | Pass | No security surface |
| IV. TDD | Pass | Test new column output |
| V. Simplicity | Pass | Modifying existing table rendering |

## Project Structure

### Source Code (repository root)

```text
python/packages/jumpstarter-kubernetes/jumpstarter_kubernetes/
├── datetime.py              # Add time_remaining function
├── leases.py                # Modify rich_add_columns/rich_add_rows for default vs wide, add REMAINING column
├── test_datetime.py         # Add time_remaining tests
└── test_leases.py           # Add column and time display tests
python/packages/jumpstarter-cli-common/jumpstarter_cli_common/
├── opt.py                   # Add "wide" to OutputMode
└── print.py                 # Pass output_mode to rich methods
```

**Structure Decision**: Modify existing lease rendering in jumpstarter-kubernetes package and CLI output handling in jumpstarter-cli-common package.
