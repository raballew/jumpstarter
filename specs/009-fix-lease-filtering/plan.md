# Implementation Plan: Fix Lease Filtering

**Branch**: `009-fix-lease-filtering` | **Date**: 2026-03-17 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-fix-lease-filtering/spec.md`

## Summary

Fix client-side lease filtering so `jmp get leases -l <selector>` returns only leases whose selector matches the user's query. The `filter_by_selector` method in `LeaseList` and the `selector_contains` function need to correctly compare the user-provided filter against each lease's stored selector.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Click (CLI), grpclib (gRPC client), pydantic (models)
**Storage**: N/A (reads from gRPC API)
**Testing**: pytest
**Target Platform**: Linux, macOS
**Project Type**: CLI tool
**Performance Goals**: N/A (client-side filtering of small lists)
**Constraints**: Must not break existing selector parsing logic
**Scale/Scope**: Fix in `jumpstarter/client/selectors.py` and `jumpstarter/client/grpc.py`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Code | Pass | Bug fix with clear scope |
| II. Minimal Dependencies | Pass | No new dependencies |
| III. Secure Coding | Pass | No security surface change |
| IV. TDD | Pass | Will write failing tests first |
| V. Simplicity | Pass | Fixing existing logic, not adding abstractions |

## Project Structure

### Documentation (this feature)

```text
specs/009-fix-lease-filtering/
├── plan.md
├── spec.md
├── research.md
└── data-model.md
```

### Source Code (repository root)

```text
python/packages/jumpstarter/jumpstarter/client/
├── selectors.py          # selector_contains() - fix matching logic
├── selectors_test.py     # Add/fix test cases for filtering
└── grpc.py               # LeaseList.filter_by_selector() - verify usage
```

**Structure Decision**: This is a bug fix in existing files. No new files or directories needed beyond test additions.
