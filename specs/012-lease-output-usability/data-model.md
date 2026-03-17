# Data Model: Improve Lease Output Usability

## Entities

### Lease (display model)

Default columns:
- **NAME**: Lease UUID
- **CLIENT**: Client name from spec.client
- **EXPORTER**: Exporter name from status.exporter
- **REMAINING**: Computed as (begin_time + duration) - now, formatted as "Xh Ym"

Wide columns (all of the above plus):
- **SELECTOR**: Comma-separated matchLabels
- **DURATION**: Raw duration string
- **STATUS**: "InProgress" or "Ended"
- **REASON**: Last condition reason
- **BEGIN**: begin_time
- **END**: end_time
- **AGE**: Time since creation

## Remaining Time States

| State | Display |
|-------|---------|
| Active, > 1 hour | "Xh Ym" |
| Active, < 1 hour | "Xm" |
| Active, < 1 minute | "<1m" |
| Expired | "Expired" |
| Pending (no begin_time) | "-" |
| No duration set | "-" |
