# Security

- Default serializer is JSON (no pickle by default)
- Workers execute only **registered** job names
- Redact sensitive keys in logs/CLI/failed-job payloads
- Treat queue payloads as untrusted input
- Do not expose monitoring endpoints publicly without auth
- Report vulnerabilities per [SECURITY.md](../SECURITY.md)
