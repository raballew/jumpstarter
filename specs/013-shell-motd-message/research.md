# Research: Shell MOTD Message

## MOTD Display Mechanism

**Decision**: Print MOTD to stdout in `launch_shell()` before spawning the shell subprocess, only when no command is provided (interactive mode).

**Rationale**: The shell is a real subprocess (bash/zsh/fish). Printing before launch is the simplest approach and mirrors how SSH MOTD works. The `command` parameter already distinguishes interactive vs non-interactive usage.

**Alternatives considered**:
- Shell RC file injection: Complex, fragile, and shell-specific.
- Environment variable: Would require the shell to display it, adding complexity.

## MOTD Configuration

**Decision**: Add an optional `motd` string field to `ExporterConfigV1Alpha1`.

**Rationale**: The exporter config is the natural place for admin-controlled per-device information. The config is already loaded when the exporter starts.

**Alternatives considered**:
- Kubernetes annotations on the exporter CRD: More complex, requires controller changes.
- Separate MOTD file: Unnecessary indirection for a simple text field.

## MOTD Transport

**Decision**: Include MOTD in session metadata returned during gRPC session establishment.

**Rationale**: The client already establishes a session with the exporter. Adding a field to the session response is the simplest transport mechanism.

**Alternatives considered**:
- New gRPC endpoint: Over-engineering for a single text field.
- Controller API: Would require controller changes and additional round-trip.
