# Research: StorageMux Auto-Detect Compression

## Existing Flasher Detection Logic

**Decision**: Locate and reuse the Flasher driver's compression detection logic.

**Rationale**: The Flasher driver already auto-detects .xz/.gz from URL extensions. The same logic should be shared with StorageMux drivers to ensure consistent behavior.

**Alternatives considered**:
- Duplicate the logic in each driver: Violates DRY.
- Content-type sniffing: Unreliable for presigned URLs and local files.

## Extension-to-Compression Mapping

**Decision**: Map extensions to compression formats: `.xz` -> xz, `.gz` -> gzip, `.bz2` -> bzip2, `.zst` -> zstd.

**Rationale**: These are the standard compression extensions used in Linux image distribution.

**Alternatives considered**:
- Magic number detection: More robust but requires reading file headers, adds complexity.

## URL Query Parameter Handling

**Decision**: Strip query parameters and fragment identifiers before extension detection using `urllib.parse.urlparse`.

**Rationale**: Presigned URLs (AWS S3, etc.) have parameters like `?Expires=...&Signature=...` that would break extension detection. Fragment identifiers (#section) could also interfere.

**Alternatives considered**: None -- this is the standard approach.

## Edge Case Handling

### Double Extensions (.tar.xz)

**Decision**: Extract only the final extension for compression detection.

**Rationale**: The compression format is determined by the outermost layer. `.tar.xz` means xz-compressed tar archive, so `.xz` is the relevant compression.

**Implementation**: Use `os.path.splitext()` or similar to get the final extension.

### Unrecognized Extensions

**Decision**: Return None for extensions not in the supported list (.xz, .gz, .bz2, .zst).

**Rationale**: Graceful degradation - treat as uncompressed rather than failing.

### Case Sensitivity

**Decision**: Convert extensions to lowercase before matching.

**Rationale**: File systems and URLs may use mixed case (.XZ, .Xz, .xz). Normalize for consistent behavior.

### Malformed URLs

**Decision**: Handle URL parsing errors gracefully, defaulting to None.

**Rationale**: Invalid URLs should not crash the detection logic. Fall back to no compression.
