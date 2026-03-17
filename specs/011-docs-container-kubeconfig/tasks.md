# Tasks: Add Kubeconfig Mount to Container Docs

**Branch**: `011-docs-container-kubeconfig` | **Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)

## Implementation Strategy

This is a documentation-only change with no code or tests involved. The strategy is to update the container run examples in the packages.md documentation file to include the kubeconfig volume mount following the existing pattern used for the Jumpstarter config mount.

Since this is a documentation fix with no code changes, TDD does not apply. Manual verification will ensure the documentation builds correctly and the examples are accurate.

## Task List

### Phase 1: Documentation Update

- [ ] [T1.1] [P1] [US1] Update basic container run examples to include kubeconfig mount in `/var/home/raballew/code/jumpstarter/python/docs/source/getting-started/installation/packages.md` (lines 224-237)
- [ ] [T1.2] [P1] [US1] Update alias examples to include kubeconfig mount in `/var/home/raballew/code/jumpstarter/python/docs/source/getting-started/installation/packages.md` (lines 247-262)
- [ ] [T1.3] [P1] [US1] Update privileged mode examples to include kubeconfig mount in `/var/home/raballew/code/jumpstarter/python/docs/source/getting-started/installation/packages.md` (lines 278-295)
- [ ] [T1.4] [P1] [US1] Add note explaining kubeconfig mount is needed for Kubernetes-dependent commands in `/var/home/raballew/code/jumpstarter/python/docs/source/getting-started/installation/packages.md` before the container examples section (around line 220)
- [ ] [T1.5] [P1] [US1] Add note about non-default kubeconfig locations (KUBECONFIG env var) and rootless container considerations in `/var/home/raballew/code/jumpstarter/python/docs/source/getting-started/installation/packages.md` near the kubeconfig mount examples

**Checkpoint**: All container run examples include kubeconfig mount with explanatory notes

### Phase 2: Verification and Polish

- [ ] [T2.1] [P2] Verify documentation builds without errors by running `make docs` from repository root
- [ ] [T2.2] [P2] Review rendered documentation to ensure kubeconfig mount is properly displayed in all examples

**Checkpoint**: Documentation builds successfully and examples are clear

## Dependencies & Execution Order

### Sequential Tasks
- T2.1 depends on T1.1, T1.2, T1.3, T1.4, T1.5 (all doc updates must be complete before building)
- T2.2 depends on T2.1 (can only review rendered docs after build succeeds)

### Parallel Tasks
- T1.1, T1.2, T1.3, T1.4, T1.5 are all in the same file but different sections, can be edited together

## Task Details

### User Story 1: Run jmp in a container with kubeconfig access

**Tasks**: T1.1, T1.2, T1.3, T1.4, T1.5

**Acceptance**:
- All container run examples include `-v "${HOME}/.kube/config:/root/.kube/config":z`
- Documentation includes note about kubeconfig mount purpose
- Documentation includes note about edge cases (KUBECONFIG env var, rootless containers)
- User can copy-paste examples and access Kubernetes from container

**Testing**: Manual verification by following the updated documentation and running `jmp get exporters` in a container with valid kubeconfig
