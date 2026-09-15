# ADR-0002: Adapters are plugins

## Status

Accepted

## Context

The community will need backends (RQ, Dramatiq, SQS) and integrations without forking this repository.

## Decision

Use Python packaging entry points (`importlib.metadata.entry_points`) for backends, schedulers, serializers, storage, locks, and middleware. Built-in adapters register the same way as third-party ones.

## Consequences

- `pip install workloom-sqs` can expose `backend="sqs"` without core changes.
- Discovery happens at configuration time, not import time for optional heavy deps where practical.
