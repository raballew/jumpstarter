# Implementation Plan: Shell MOTD Message

**Branch**: `013-shell-motd-message` | **Date**: 2026-03-17 | **Spec**: [spec.md](spec.md)

## Summary

Print a welcome message (exporter name + optional admin-configured MOTD) to stdout before launching the shell subprocess in `launch_shell()`. The MOTD text comes from the exporter configuration and is transmitted via existing session metadata.

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
└── utils.py                 # Add MOTD print before shell launch
python/packages/jumpstarter/jumpstarter/config/
└── exporter.py              # Add optional motd field to config model
python/packages/jumpstarter-cli/jumpstarter_cli/
└── shell.py                 # Pass MOTD context to launch_shell
```

**Structure Decision**: Modify existing files; no new modules needed.
