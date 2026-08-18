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

`SchemaOrgBase` owns JSON-LD mechanics. `Thing`, `CreativeWork`, and
`SoftwareSourceCode` are stable information-model concepts. `CodeMeta` is the
canonical open document model, and `CodeMetaV3` specializes it by requiring
the v3 context. A future version binding can specialize `CodeMeta` in the same
way without changing the core hierarchy.

`CodeMeta` defaults to v3 but preserves an explicitly supplied string, object,
array, or null context. Known vocabulary terms are typed; unknown properties
remain raw JSON-compatible values and survive round-trip serialization.

`CodeMeta.from_jsonld` is a pure parse (`model_validate`) — it preserves the
declared `@context` verbatim and performs no migration or normalization. Use
it for canonical CodeMeta documents.

`CodeMeta.from_legacy_jsonld` is the explicit migration path for legacy input
that uses prefix-qualified keys (`schema:name`) or pre-v3 property names
(`creator`, `embargoDate`, `contIntegration`). It applies
`normalize_jsonld_context` (flattens dict `@context` prefixes, removes the
dict context, backfills v3) and `migrate_legacy_codemeta` (renames legacy
keys), then parses as v3 and adapts to `CodeMeta`. This is intentionally lossy:
the dict `@context` is removed after prefix flattening.

Python uses snake_case names and JSON-LD serialization uses CodeMeta/schema.org
aliases:

```python
from pydantic_codemeta import CodeMeta

model = CodeMeta(
    name="Example",
    code_repository="https://example.org/repository",
    date_published="2026-08-18",
)
assert model.to_jsonld()["codeRepository"] == "https://example.org/repository"
```

Concrete models use one constrained `@type`; multi-valued `@type` is outside
the typed-model scope. See `docs/specs/codemeta-pydantic-v2.md` for the full
context, migration, date, collision, and round-trip contracts.

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
