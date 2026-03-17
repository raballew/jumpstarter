# Research: Improve Lease Output Usability

## Relative Time Formatting

**Decision**: Compute remaining time as `(begin_time + duration) - now` and format as "Xh Ym" style. Use `end_time` if available.

**Rationale**: This matches the kubectl style for AGE columns. The `time_since` helper already exists in `jumpstarter_kubernetes/datetime.py` and can be adapted.

**Alternatives considered**:
- Absolute timestamp: Rejected per clarification -- users want relative time.
- Countdown timer: Over-engineering for a static table display.

## Default vs Wide Column Sets

**Decision**: Default shows NAME, CLIENT, EXPORTER, REMAINING. Wide (`-o wide`) shows all columns.

**Rationale**: The 4 default columns answer the most common questions: "what lease?", "who has it?", "which device?", "how long left?". The `-o wide` flag is already supported by the output system.

**Alternatives considered**:
- Making columns configurable via flags: Over-engineering for current needs.
