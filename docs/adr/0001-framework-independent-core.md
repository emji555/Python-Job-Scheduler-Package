# ADR-0001: Framework-independent core

## Status

Accepted

## Context

Python background-job tooling is often tightly coupled to a web framework (Django) or a single engine (Celery). Application code then cannot move between frameworks or brokers without rewrites.

## Decision

The core package (`package_name`) must not import Django, Flask, FastAPI, Celery, RQ, Redis, or SQLAlchemy. Frameworks and engines are optional integrations/adapters.

## Consequences

- Core installs remain lightweight.
- Integrations live under `package_name.integrations.*` or third-party packages.
- CI verifies that importing core does not pull optional engines.
