# pydantic-codemeta

Pydantic v2 models for parsing, validating, and serializing [CodeMeta](https://codemeta.github.io/) JSON-LD metadata, with typed Python APIs and round-trip preservation of unknown properties.

The package provides a typed representation of common CodeMeta and schema.org terms while preserving unknown JSON-LD properties during round trips.

## Features

- Typed CodeMeta and schema.org models built on Pydantic v2
- JSON-LD aliases such as `@context`, `@type`, and `codeRepository`
- Preservation of unknown JSON-compatible properties
- Explicit legacy CodeMeta migration without implicit document rewriting
- Typed CodeMeta 3.0 models with strict @context validation

## Requirements

- Python 3.11 or newer
- Pydantic 2.x

## Installation

```bash
python -m pip install pydantic-codemeta
```

## Usage

Parse a CodeMeta document into a validated model and serialize it back to
JSON-LD:

```python
from pydantic_codemeta import CodeMeta

document = {
    "@context": "https://w3id.org/codemeta/3.0",
    "@type": "SoftwareSourceCode",
    "name": "Example",
    "codeRepository": "https://example.org/repository",
}

metadata = CodeMeta.from_jsonld(document)

assert metadata.code_repository == "https://example.org/repository"
assert metadata.to_jsonld()["codeRepository"] == document["codeRepository"]
```

Python attributes use snake_case names. `to_jsonld()` emits the corresponding
CodeMeta and schema.org aliases.

### Parsing Behavior

- `CodeMeta.from_jsonld()` validates canonical CodeMeta 3.0 without rewriting it.
- `CodeMeta.from_legacy_jsonld()` explicitly migrates supported legacy forms.
- Unknown JSON-compatible properties survive parse and serialization round trips.

See the
[model specification](https://github.com/SciCodes/pydantic-codemeta/blob/main/docs/specs/codemeta-pydantic-v2.md)
for the complete field, context, migration, date, collision, and round-trip
contracts.

## Development

Install [uv](https://docs.astral.sh/uv/), then create the development
environment and run the test suite:

```bash
uv sync --extra test
uv run python -m pytest -q -s
```

Build and validate the distribution artifacts:

```bash
uv build
uv run twine check dist/*
```

Docker-based checks are also available:

```bash
make docker-test
make docker-package
```

## TestPyPI rehearsal

A full TestPyPI rehearsal builds, validates, and uploads the package without
touching production PyPI. Configure `~/.pypirc` with TestPyPI credentials:

```ini
[testpypi]
username = __token__
password = pypi-<your-testpypi-token>
```

Then run:

```bash
make release-test
```

This runs `clean`, `test`, `package`, `check`, and `publish-test` (uploads to
TestPyPI). After uploading, verify the package installs from TestPyPI:

```bash
make smoke-test
```

Production PyPI releases are published by the GitHub Actions release workflow
using PyPI Trusted Publishing. Do not use `make publish` for production
releases.

## Contributing

Issues and pull requests are welcome in the
[GitHub repository](https://github.com/SciCodes/pydantic-codemeta). Include
focused tests for behavioral changes and preserve the contracts documented in
the model specification.

## License

`pydantic-codemeta` is distributed under the
[MIT License](https://github.com/SciCodes/pydantic-codemeta/blob/main/LICENSE).
