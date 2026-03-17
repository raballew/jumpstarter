# Feature Specification: Add Kubeconfig Mount to Container Docs

**Feature Branch**: `011-docs-container-kubeconfig`
**Created**: 2026-03-17
**Status**: Draft
**Input**: User description: "Container docs missing kubeconfig mount - issue #37"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run jmp in a container with kubeconfig access (Priority: P1)

A user follows the documentation to run Jumpstarter in a container (Docker/Podman) and needs access to their Kubernetes cluster. The current docs omit the `-v` mount for `~/.kube/config`, causing `jmp` commands that interact with Kubernetes to fail silently or with confusing errors.

**Why this priority**: Without this mount, container-based usage is broken for any Kubernetes-dependent workflow, which is the primary use case.

**Independent Test**: Follow the updated docs to run `jmp` in a container and verify that `jmp get exporters` works when the user has a valid kubeconfig.

**Acceptance Scenarios**:

1. **Given** the documentation example for running jmp in a container, **When** a user copies and runs the command, **Then** the kubeconfig is available inside the container.
2. **Given** a user without a kubeconfig file, **When** they follow the docs, **Then** the command still works (the mount is optional or clearly documented as conditional).

---

### Edge Cases

- What if the kubeconfig is at a non-default location (set via KUBECONFIG env var)?
- What about rootless container runtimes where paths differ?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The container run example in the documentation MUST include a volume mount for the kubeconfig file.
- **FR-002**: The documentation MUST note that the kubeconfig mount is needed for commands that interact with Kubernetes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The documented container run command includes kubeconfig mount.
- **SC-002**: A user following the docs can successfully run Kubernetes-dependent jmp commands from inside the container.
