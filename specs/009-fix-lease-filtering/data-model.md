# Data Model: Fix Lease Filtering

## Entities

### Lease

- **selector**: String containing comma-separated key=value pairs (e.g., `name=my-exporter,board=arm`)
- **Parsed as**: `matchLabels` dict (key -> value) and `matchExpressions` list

### Label Selector (user filter)

- **Format**: `-l key=value,key2=value2`
- **Parsed as**: Same structure as lease selector

## Matching Logic

A lease matches a user filter when:
1. All key=value pairs in the user filter exist in the lease's selector matchLabels
2. The lease's selector may contain additional labels beyond the filter (superset match)

## State Transitions

N/A -- stateless filtering operation.
