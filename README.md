# codemeta-pydantic

CodeMeta-focused schema.org models built with Pydantic v2.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- Python 3.12 (see `.python-version`)

## Quickstart (uv)

```bash
uv sync --extra test --group dev
uv run pytest -q
```

## CodeMeta model boundaries

`CodeMetaV3` is the typed/open v3 `SoftwareSourceCode` envelope and requires
the v3 context. `CodeMeta` is the canonical open model: it defaults to v3 but
preserves any explicitly supplied string context. Both preserve unknown
properties and perform no implicit migrations during direct validation.

The explicit `normalize_jsonld_context` and `migrate_legacy_codemeta` helpers
are root-only transforms. Dict-context normalization is intentionally lossy
because it removes the dict context. `CodeMeta.from_jsonld` is a one-release
compatibility shim that applies both transforms, parses v3, and adapts to
`CodeMeta`; use direct model validation when no transforms are wanted.

## Common Make Targets

```bash
make sync         # install runtime + test + dev dependencies with uv
make test         # run tests
make clean        # remove build/test artifacts
make package      # build sdist and wheel into dist/
make check        # verify distributions with twine
make publish-test # upload to TestPyPI
make publish      # upload to PyPI
make docker-test  # run tests in container via docker compose
make docker-package # build package artifacts in container
```

## Container Workflow

The container installs dependencies into the project virtual environment and activates it via `PATH=/app/.venv/bin:$PATH`.
When using Docker Compose with a bind mount, an anonymous volume is mounted at `/app/.venv` so the container environment is not overwritten by host files.
The Dockerfile uses BuildKit cache mounts for uv, and separates dependency installation from project installation to improve rebuild times.

For reproducible dependency resolution, generate and commit a lockfile:

```bash
uv lock
```

Build once:

```bash
docker build -t codemeta-pydantic:local .
```

Run tests in container:

```bash
docker compose run --rm test
```

Build wheel and sdist in container:

```bash
docker compose run --rm package
```

## Publishing Notes

- `make publish-test` uploads to TestPyPI first.
- `make publish` uploads to PyPI.
- Configure credentials with environment variables or a `~/.pypirc` profile used by Twine.
