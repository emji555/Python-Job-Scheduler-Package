# Releasing

## One-time setup

1. Create the GitHub repository (example: `EXAMPLE_ORG/package-name`).
2. On **TestPyPI** → Your projects → Publishing → Trusted Publishers:
   - Owner: `EXAMPLE_ORG`
   - Repository: `package-name`
   - Workflow: `publish.yml`
   - Environment: `testpypi`
3. On **PyPI**, same settings with Environment: `pypi`.
4. In GitHub → Settings → Environments, create `testpypi` and `pypi`.
   Protect `pypi` with required reviewers.

## Release flow

```text
development → PR → CI → merge main → bump version → tag v0.x.y
  → GitHub Release → build once → TestPyPI → approved PyPI
```

### Maintainer commands

```bash
# 1. Ensure main is green
pytest && ruff check src tests && mypy && python -m build

# 2. Bump version in pyproject.toml and src/package_name/__init__.py
# 3. Update CHANGELOG.md

git add -A
git commit -m "chore: release v0.1.0"
git tag v0.1.0
git push origin main
git push origin v0.1.0
```

Creating the GitHub Release for tag `v0.1.0` triggers `publish.yml`.

Do **not** store long-lived PyPI API tokens for the normal release path.
