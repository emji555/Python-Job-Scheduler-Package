# ADR-0005: Explicit backend capabilities

## Status

Accepted

## Context

Pretending every backend supports delays, cancellation, priorities, and results leads to silent incorrect behavior.

## Decision

Each backend exposes `BackendCapabilities`. Calling an unsupported feature raises `UnsupportedCapabilityError`.

## Consequences

- Clearer failures and documentation matrices.
- Application authors can feature-detect.
- Contract tests assert capability claims.
