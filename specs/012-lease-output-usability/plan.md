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
**Scale/Scope**: Changes in `jumpstarter-kubernetes` (lease model) and `jumpstarter/client/grpc.py` (LeaseList)

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
└── leases.py                # Modify rich_add_columns/rich_add_rows for default vs wide
python/packages/jumpstarter/jumpstarter/client/
└── grpc.py                  # Lease/LeaseList rich rendering
python/packages/jumpstarter-cli/jumpstarter_cli/
└── get.py                   # Pass output mode to model_print
```

**Structure Decision**: Modify existing lease rendering in two packages.
