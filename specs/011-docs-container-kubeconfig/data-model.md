# Data Model: Add Kubeconfig Mount to Container Docs

**Branch**: `011-docs-container-kubeconfig` | **Spec**: [spec.md](spec.md)

## Overview

This is a documentation-only change with no data structures, API contracts, or code models. The data model document exists for completeness but contains no technical data structures.

## Documentation Structure

### Container Run Examples

The documentation examples follow this pattern:

```bash
docker run -it --rm \
  -v "${HOME}/.config/jumpstarter/:/root/.config/jumpstarter":z \
  -v "${HOME}/.kube/config:/root/.kube/config":z \
  ghcr.io/jumpstarter-dev/jumpstarter:latest \
  jmp <command>
```

**Key Elements**:
- `-v "${HOME}/.config/jumpstarter/:/root/.config/jumpstarter":z` - Jumpstarter config mount (existing)
- `-v "${HOME}/.kube/config:/root/.kube/config":z` - Kubeconfig mount (new)
- `:z` suffix - SELinux relabeling flag for Fedora/RHEL systems

### Mount Path Mapping

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `${HOME}/.config/jumpstarter/` | `/root/.config/jumpstarter` | Jumpstarter configuration |
| `${HOME}/.kube/config` | `/root/.kube/config` | Kubernetes cluster configuration |

### Edge Cases

**Non-default kubeconfig location**:
- Users with `KUBECONFIG` environment variable set to non-default path
- Solution: Document both the standard mount and KUBECONFIG env var passthrough

**Rootless containers**:
- Podman rootless mode may require different path mappings
- Solution: Add note that paths should be adjusted for rootless scenarios

## Validation Rules

N/A - Documentation only, no runtime validation

## Migration Path

N/A - Documentation only, no migration needed

## Notes

This change is purely additive to existing documentation. No existing functionality is modified or removed.
