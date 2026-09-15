# ADR-0007: PyPI Trusted Publishing

## Status

Accepted

## Context

Long-lived PyPI API tokens in CI secrets are a supply-chain risk.

## Decision

Release workflows publish via GitHub Actions OIDC Trusted Publishing to TestPyPI and PyPI. Artifacts are built once and reused. Production publish requires environment protection.

## Consequences

- Maintainers configure Trusted Publishers once on PyPI/TestPyPI.
- No normal-path long-lived API tokens.
- Releases are intentional (tag/GitHub Release driven).
