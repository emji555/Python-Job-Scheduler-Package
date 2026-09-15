# ADR-0006: src layout

## Status

Accepted

## Context

Editable installs and accidental imports of the working tree are common packaging pitfalls.

## Decision

Use a `src/` layout with Hatchling as the build backend.

## Consequences

- Tests import the installed/editable package, not a random tree root.
- Packaging is standards-based (`pyproject.toml` only).
