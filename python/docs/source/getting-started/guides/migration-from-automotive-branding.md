# Migration Guide: Domain-Neutral Branding

This guide is for existing Jumpstarter users who adopted the platform when it
was primarily presented as an automotive testing tool. It explains what changed
and confirms that no action is required on your part.

## What Changed

Jumpstarter's documentation and driver categorization have been updated to
reflect the platform's applicability across multiple industries, not just
automotive. The platform now presents itself as a generic device testing
framework that serves automotive, robotics, edge AI, industrial IoT, and any
other vertical shipping software to devices.

### Documentation Changes

- The **introduction page** no longer frames Jumpstarter as an automotive
  tool. It now describes the platform generically and lists multiple industry
  verticals as example use cases.
- The **driver documentation** renamed the "Automotive Diagnostics Drivers"
  section to "Diagnostics Protocol Drivers" to reflect that protocols like
  UDS, DoIP, and SOME/IP are used beyond automotive.
- **Vertical-specific quick-start guides** were added for automotive,
  robotics, and edge AI.

### What Did NOT Change

- **CLI commands**: The `jmp` CLI and all subcommands are unchanged. No
  commands, flags, or output messages were modified.
- **Driver packages**: All driver packages (`jumpstarter-driver-uds-doip`,
  `jumpstarter-driver-can`, `jumpstarter-driver-someip`, etc.) retain their
  names, APIs, and functionality.
- **Exporter configurations**: Your existing exporter YAML files continue
  to work without modification.
- **Operator/Controller**: The Kubernetes operator install path is unchanged.
  The same operator serves all verticals.
- **Python APIs**: No Python API changes. Your test scripts and automation
  code continue to work.
- **Example applications**: The `python/examples/automotive/` example
  remains and continues to work.

## Action Required

**None.** This is a documentation-only change. Your existing workflows,
configurations, test scripts, and CI/CD pipelines require no modifications.

## Questions

If you have questions about this change, reach out through the community
channels:

- [Matrix Chat](https://matrix.to/#/#jumpstarter:matrix.org)
- [Weekly Meeting](https://meet.google.com/gzd-hhbd-hpu)
- [Meeting Notes](https://etherpad.jumpstarter.dev/pad-lister)
