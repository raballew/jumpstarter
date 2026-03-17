# Implementation Plan: Lease Create/Delete Validation

**Branch**: `017-lease-create-delete-validation` | **Date**: 2026-03-17 | **Spec**: [spec.md](spec.md)

## Summary

Add client-side validation to `jmp create lease` to require a selector, and improve `jmp delete leases` to report when a lease is not found or already deleted.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Click (CLI), grpclib (gRPC)
**Storage**: N/A
**Testing**: pytest
**Target Platform**: Linux, macOS
**Project Type**: CLI tool
**Performance Goals**: N/A
**Constraints**: Must match `jmp shell` error style for selector validation
**Scale/Scope**: Changes in `create.py` and `delete.py` in jumpstarter-cli

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Code | Pass | Input validation at boundaries |
| II. Minimal Dependencies | Pass | No new deps |
| III. Secure Coding | Pass | Validates input at system boundary (constitution III.1) |
| IV. TDD | Pass | Test validation error cases |
| V. Simplicity | Pass | Simple pre-flight checks |

## Project Structure

### Source Code (repository root)

```text
python/packages/jumpstarter-cli/jumpstarter_cli/
├── create.py           # Add selector validation before API call
├── create_test.py      # Test missing selector error
├── delete.py           # Check API response for not-found
└── delete_test.py      # Test already-deleted error
```

**Structure Decision**: Modify existing create/delete command files.

## File Modifications

All file paths are absolute and tested:
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/exceptions.py` - New exception type
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/grpc.py` - Exception translation
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/config/client.py` - Delete method
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/delete.py` - CLI command
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/delete_test.py` - New test file
