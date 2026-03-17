# Research: Add Kubeconfig Mount to Container Docs

## Container Volume Mount Pattern

**Decision**: Add `-v "${HOME}/.kube/config:/root/.kube/config":z` to the existing container run example.

**Rationale**: This follows the same pattern already used for the Jumpstarter config mount (`-v "${HOME}/.config/jumpstarter/:/root/.config/jumpstarter":z`). The `:z` suffix is needed for SELinux relabeling on Fedora/RHEL systems.

**Alternatives considered**:
- Mounting the entire `.kube/` directory: Rejected, only the config file is needed and mounting the full directory could expose cache/credentials.
- Using KUBECONFIG env var passthrough: Could be added as a note for non-default locations but the volume mount is the primary fix.
