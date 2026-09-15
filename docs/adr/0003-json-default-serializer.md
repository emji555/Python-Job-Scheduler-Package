# ADR-0003: JSON is the default serializer

## Status

Accepted

## Context

Pickle enables arbitrary code execution and fragile cross-version compatibility. Distributed and security-sensitive systems need a safer default.

## Decision

`JsonSerializer` is the default. A `Serializer` protocol allows registered alternatives. Arbitrary Python objects are rejected unless JSON-safe (or explicitly handled by a custom serializer).

## Consequences

- Payloads must be JSON-serializable by default.
- Better security posture and clearer trust boundaries.
- Some advanced object graphs require application-side DTO mapping.
