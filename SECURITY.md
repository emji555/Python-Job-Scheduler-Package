# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 0.1.x | yes |

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security vulnerabilities.

Email: `security@example.com` (replace with the real maintainer contact before public release)

Include:

- Package version
- Affected component (core, backend adapter, CLI, integration)
- Reproduction steps
- Impact assessment

You should receive an acknowledgement within 7 days.

## Trust boundaries

- Queue payloads are treated as **untrusted** until validated against the **job registry**.
- JSON is the default serializer; pickle is not used by default.
- CLI and failed-job listings apply redaction hooks for sensitive keys.
- Monitoring/dashboard integrations must not be exposed publicly without authentication.
