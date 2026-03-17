# Data Model: Shell MOTD Message

## Entities

### ExporterConfig (modified)

- **motd**: Optional string field. When set, displayed to users connecting via `jmp shell`.

### Session Metadata (modified)

- **motd**: Optional string field transmitted from exporter to client during session setup.

## MOTD Display Format

```
Connected to exporter: <exporter-name>
<admin-configured MOTD text, if present>
```

When no MOTD is configured, only the first line is shown.
