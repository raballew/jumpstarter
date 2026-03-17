# Implementation Plan: Shell MOTD Message

**Branch**: `013-shell-motd-message` | **Date**: 2026-03-17 | **Spec**: [spec.md](spec.md)

## Summary

Print a welcome message (exporter name + optional admin-configured MOTD) to stdout before launching the shell subprocess in `launch_shell()`. The MOTD text comes from the exporter configuration and is transmitted via existing session metadata.

**Data Flow**: ExporterConfig.motd → Session metadata (during gRPC session establishment) → shell.py retrieves from session → launch_shell() displays before spawning subprocess.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Click (CLI), grpclib (gRPC)
**Storage**: N/A
**Testing**: pytest
**Target Platform**: Linux, macOS
**Project Type**: CLI tool
**Performance Goals**: N/A
**Constraints**: Must not print MOTD for non-interactive command execution
**Scale/Scope**: Changes in `jumpstarter/common/utils.py` (launch_shell), exporter config model, and session metadata

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Code | Pass | Small addition to launch_shell |
| II. Minimal Dependencies | Pass | No new deps |
| III. Secure Coding | Pass | MOTD is admin-configured, not user-controlled |
| IV. TDD | Pass | Test MOTD output in launch_shell |
| V. Simplicity | Pass | Print to stdout before subprocess |

## Project Structure

### Source Code (repository root)

```text
python/packages/jumpstarter/jumpstarter/common/
├── utils.py                 # Add MOTD print before shell launch
└── session.py               # Add motd field to session metadata model
python/packages/jumpstarter/jumpstarter/config/
└── exporter.py              # Add optional motd field to config model
python/packages/jumpstarter/jumpstarter/
└── exporter.py              # Include motd from config in session metadata response
python/packages/jumpstarter-cli/jumpstarter_cli/
└── shell.py                 # Pass MOTD context to launch_shell
```

**Structure Decision**: Modify existing files; no new modules needed.

## Test File Locations

Following the project's test convention (co-located `*_test.py` files):
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/config/exporter_test.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/session_test.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/utils_test.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell_test.py`
- `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter-cli/jumpstarter_cli/shell_e2e_test.py`

## Requirements Traceability

| Requirement | Success Criteria | Tasks |
|-------------|------------------|-------|
| FR-001: Print exporter name | SC-001: Users see exporter name | T2.5, T2.6, T2.7, T2.8, T2.9, T2.10 |
| FR-002: Display admin MOTD | SC-002: Admin MOTD appears | T1.1-T1.7, T3.1-T3.9 |
| FR-003: Print before subprocess | SC-001: Name shown at start | T2.1, T2.3, T2.4 |
| FR-004: No MOTD for commands | SC-003: Commands unaffected | T2.2, T2.11, T2.12, T4.5 |
