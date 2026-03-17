# Implementation Plan: Add Kubeconfig Mount to Container Docs

**Branch**: `011-docs-container-kubeconfig` | **Date**: 2026-03-17 | **Spec**: [spec.md](spec.md)

## Summary

Add kubeconfig volume mount to the container run example in the documentation so users can run Kubernetes-dependent jmp commands from inside a container.

## Technical Context

**Language/Version**: Markdown (documentation)
**Primary Dependencies**: N/A
**Storage**: N/A
**Testing**: Manual verification of doc build
**Target Platform**: Documentation site
**Project Type**: Documentation fix
**Performance Goals**: N/A
**Constraints**: Must not break existing doc build
**Scale/Scope**: Single file edit in `python/docs/source/getting-started/installation/packages.md`

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Code | Pass | Docs change only |
| II. Minimal Dependencies | Pass | No deps |
| III. Secure Coding | Pass | No security impact |
| IV. TDD | N/A | Documentation change |
| V. Simplicity | Pass | One-line addition |

## Project Structure

### Source Code (repository root)

```text
python/docs/source/getting-started/installation/
└── packages.md    # Add kubeconfig mount to container run example
```

**Structure Decision**: Single file documentation edit.
