# Data Model: Better Exception Handling

## Overview

This feature does not introduce new data models or storage entities. It enhances existing exception handling with user-friendly message formatting.

## Key Entities

### ExceptionMessage

A runtime structure (not persisted) representing a user-friendly error message.

**Attributes**:
- `message`: String - The main error description
- `suggested_action`: Optional[String] - Actionable guidance for the user
- `exception_type`: String - The Python exception class name (for debugging)

**Example**:
```python
{
    "message": "TLS certificate verification failed for example.com",
    "suggested_action": "Use --insecure to skip verification",
    "exception_type": "ClientConnectorCertificateError"
}
```

### Exception Mapping Table

A static mapping (implemented as a dict or match statement) from exception types to messages.

**Structure**:
```python
exception_type -> (message_template, suggested_action)
```

**Examples**:
- `ConnectionRefusedError` → ("Could not connect to {host}", "Check that the endpoint is correct and reachable")
- `TimeoutError` → ("Connection timed out", "Check network connectivity")
- `grpclib.StatusCode.UNAUTHENTICATED` → ("Authentication failed", "Run 'jmp login' to re-authenticate")

## No Persistence Required

All data in this feature is ephemeral and generated at runtime. No database, file storage, or API schema changes are needed.
