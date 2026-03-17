# Research: Better Exception Handling

## Exception-to-Message Mapping

**Decision**: Map specific exception types to user-friendly messages with suggested actions.

| Exception | Friendly Message | Suggested Action |
|-----------|-----------------|------------------|
| `ClientConnectorCertificateError` | "TLS certificate verification failed for {host}" | "Use --insecure to skip verification" |
| `SSLCertVerificationError` | "TLS certificate verification failed" | "Use --insecure to skip verification" |
| `ConnectionRefusedError` | "Could not connect to {host}" | "Check that the endpoint is correct and reachable" |
| `TimeoutError` / `asyncio.TimeoutError` | "Connection timed out" | "Check network connectivity" |
| `grpc.StatusCode.UNAUTHENTICATED` | "Authentication failed" | "Run 'jmp login' to re-authenticate" |
| `grpc.StatusCode.PERMISSION_DENIED` | "Permission denied" | "Check your client credentials" |
| `FileNotFoundError` (config) | "Configuration file not found" | "Run 'jmp login' to create one" |

**Rationale**: These are the most commonly reported error scenarios from issues #57 and #175.

**Alternatives considered**:
- Rich traceback formatting: Still shows too much detail for end users.
- Sentry-style error reporting: Over-engineering for a CLI tool.

## Debug Mode

**Decision**: Use existing `--debug` or `JUMPSTARTER_DEBUG` env var to show full tracebacks.

**Rationale**: Avoids adding a new flag. The env var approach works for all commands without per-command changes.

**Alternatives considered**:
- Per-command `--verbose` flag: Would require changes to every command definition.
- Log file: Adds complexity; users can redirect stderr themselves.
