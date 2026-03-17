# Data Model: StorageMux Auto-Detect Compression

## Overview

This feature does not introduce new data models. It operates on existing driver interfaces.

## Modified Interfaces

### Compression Detection Function

```python
def detect_compression_from_url(url: str) -> str | None:
    """
    Detect compression format from URL file extension.
    
    Args:
        url: File URL or path (may include query parameters)
        
    Returns:
        Compression format ('xz', 'gz', 'bz2', 'zst') or None if uncompressed
        
    Raises:
        None (returns None for unrecognized extensions)
    """
    pass
```

### Extension Mapping

```python
COMPRESSION_EXTENSIONS = {
    '.xz': 'xz',
    '.gz': 'gz',
    '.bz2': 'bz2',
    '.zst': 'zst',
}
```

## Data Flow

1. User provides URL → 2. Strip query params → 3. Extract extension → 4. Map to compression format → 5. Pass to driver

## Validation Rules

- URL query parameters and fragments MUST be removed before extension detection
- Extension matching is case-insensitive
- Only the final extension is considered (`.tar.xz` → `.xz`)
- Explicit `--compression` flag overrides auto-detection
