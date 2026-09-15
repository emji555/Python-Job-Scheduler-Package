# Contributing

Thanks for contributing to `PACKAGE_NAME`.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
pre-commit install
pytest
```

## Guidelines

- Prefer Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
- Do not import Django/Flask/FastAPI/Celery/Redis inside core modules.
- New backends should register via entry points and pass `tests/test_backend_contract.py` patterns.
- Add/adjust tests with behavior changes.
- Update `CHANGELOG.md` for user-visible changes.

## Pull requests

Use the PR template. Ensure CI is green: lint, typecheck, tests, and package build.
