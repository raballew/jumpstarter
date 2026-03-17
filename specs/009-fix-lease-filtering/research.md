# Research: Fix Lease Filtering

## Current Behavior Analysis

**Decision**: The bug is in the interaction between `filter_by_selector` and `selector_contains`.

**Rationale**: The server-side API returns leases filtered by matchLabels, but the client-side `filter_by_selector` calls `selector_contains(lease.selector, filter_selector)` which checks if the *lease's selector* contains the *user's filter*. The issue from #29 shows that leases with different selectors are returned when filtering by a specific name. This suggests the comparison direction or parsing logic is incorrect.

**Alternatives considered**:
- Server-side fix: Not feasible without controller changes, and client-side filtering is the documented approach.
- New filtering function: Unnecessary; fixing the existing `selector_contains` logic is sufficient.

## Selector Format

**Decision**: Selectors use Kubernetes-style label selector format: `key=value,key2=value2`.

**Rationale**: The `parse_label_selector` function in `selectors.py` already handles this format. The `name=<exporter>` pattern is treated as a regular label.

**Alternatives considered**: None -- this is an established format in the codebase.
