# Research: Lease Create/Delete Validation

## Create Validation

**Decision**: Add a client-side check in `jmp create lease` that requires `--selector/-l` or `--name/-n`, matching `jmp shell` behavior.

**Rationale**: The server accepts empty selectors but creates unsatisfiable leases. Client-side validation prevents this waste.

**Alternatives considered**:
- Server-side validation: Would require controller changes; client-side is faster to implement and provides immediate feedback.

## Delete Not-Found Detection

**Decision**: Check the gRPC response status when deleting a lease. If the server returns NOT_FOUND, display "lease not found" instead of "deleted".

**Rationale**: The current code ignores the server response and always prints success. Checking the response is a minimal change.

**Alternatives considered**:
- Pre-check with GET before DELETE: Adds an extra API call; checking the DELETE response is simpler.
