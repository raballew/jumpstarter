# Data Model: Lease Create/Delete Validation

**Branch**: `017-lease-create-delete-validation`
**Spec**: [spec.md](spec.md)

## Overview

This feature adds validation constraints to existing data models without modifying their structure.

## Entities

### Lease

**Existing Model**: Defined in the jumpstarter controller, not modified by this feature.

**Validation Constraints** (enforced client-side):
- MUST have a selector (label matching criteria) OR a name reference
- Cannot be created with an empty selector

**State Transitions**:
- Active -> Deleted (via `jmp delete leases`)
- Deleted leases cannot be deleted again (server returns NOT_FOUND)

## Exception Types

### New: ResourceNotFoundError

**Purpose**: Represents a 404/NOT_FOUND response from the gRPC API when attempting to delete a non-existent lease.

**Location**: `/var/home/raballew/code/jumpstarter/python/packages/jumpstarter/jumpstarter/common/exceptions.py`

**Properties**:
- Inherits from base exception class
- Contains resource identifier (lease UUID)
- Used by delete operations to signal not-found state

**Mapping**:
- gRPC `StatusCode.NOT_FOUND` -> `ResourceNotFoundError`
- Handled in `translate_grpc_exceptions` function

## API Interactions

### Create Lease
- **Validation Point**: Client-side before API call
- **Invalid Input**: Empty selector
- **Response**: Error message, no API call made

### Delete Lease
- **Validation Point**: Server response status code
- **Success**: Lease deleted, status OK
- **Not Found**: `StatusCode.NOT_FOUND` -> `ResourceNotFoundError`
- **Error Handling**:
  - Single delete: Display error, exit with error code
  - Bulk delete (--all, --selector): Log warning, continue

## No Schema Changes

This feature does not modify:
- Lease protobuf definitions
- Database schemas
- API contracts

All changes are client-side validation and error handling logic.
