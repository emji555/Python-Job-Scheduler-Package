# ADR-0004: Do not reimplement Celery

## Status

Accepted

## Context

Building a new distributed broker is expensive, risky, and unnecessary when mature engines already exist.

## Decision

`PACKAGE_NAME` is an abstraction layer. `CeleryBackend` delegates to Celery. Future backends wrap RQ, Dramatiq, SQS, etc. In-process `EagerBackend` / `MemoryBackend` cover tests and local development.

## Consequences

- Production reliability inherits from the chosen engine.
- Capability matrix documents feature gaps per backend.
- Core focuses on DX, envelope, retries semantics, scheduling API, locks, and observability interfaces.
