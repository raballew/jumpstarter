# Implementation Plan: Better Exception Handling

**Branch**: `015-better-exception-handling` | **Date**: 2026-03-17 | **Spec**: [spec.md](spec.md)

## Summary

Add a top-level exception handler to the CLI that catches common exceptions (connection errors, TLS/SSL errors, auth errors, timeouts) and displays user-friendly messages instead of stack traces. Also covers issue #175 (cert error stack trace).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Click (CLI), aiohttp, grpclib
**Storage**: N/A
**Testing**: pytest
**Target Platform**: Linux, macOS
**Project Type**: CLI tool
**Performance Goals**: N/A
**Constraints**: Must not suppress errors in debug mode; must not change exit codes
**Scale/Scope**: Top-level handler in `jmp.py` + exception mapping module

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Code | Pass | Centralized error handling |
| II. Minimal Dependencies | Pass | No new deps |
| III. Secure Coding | Pass | Prevents leaking stack traces to users (constitution III.5) |
| IV. TDD | Pass | Test each exception type produces friendly message |
| V. Simplicity | Pass | Simple exception-to-message mapping |

## Project Structure

### Source Code (repository root)

```text
python/packages/jumpstarter-cli-common/jumpstarter_cli_common/
├── exceptions.py       # Extend existing exception handling with friendly messages
└── exceptions_test.py  # Test exception-to-message mapping
python/packages/jumpstarter-cli/jumpstarter_cli/
└── jmp.py              # Wire up top-level handler
```

**Structure Decision**: Extend existing `exceptions.py` in cli-common rather than creating a new module.
