# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-15

### Added

- Initial Workloom release (`workloom`) with Laravel-inspired jobs API
- Core job decorator, registry, envelope, JSON serializer, dispatch API, and job handles
- Eager and Memory backends plus Celery adapter
- Retry policies, middleware, lifecycle events, failed-job storage API
- Scheduler fluent API with timezone-aware cron, `without_overlapping`, `on_one_server`
- Memory and Redis lock backends
- Chain/group pipeline primitives
- Plugin discovery via entry points with built-in fallbacks
- CLI (`doctor`, worker, schedule, failed jobs)
- Optional Django, FastAPI, and Flask integrations
- Docs, ADRs, examples, GitHub Actions, and PyPI Trusted Publishing workflows
