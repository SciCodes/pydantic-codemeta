# Contributing to pydantic-codemeta

Contributions are welcome. This guide describes how to set up a development
environment, run tests, format code, and propose changes.

## Prerequisites

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) for dependency management
- [Docker](https://www.docker.com/) (optional, for Docker-based checks)

## Development setup

Clone the repository and create the development environment:

```bash
git clone https://github.com/SciCodes/pydantic-codemeta.git
cd pydantic-codemeta
uv sync
```

This installs the package with all development and test dependencies.

## Running tests

Run the test suite:

```bash
make test
```

Or directly with uv:

```bash
uv run python -m pytest -q -s
```

## Formatting and linting

Format Python, Markdown, and JSON before submitting a pull request:

```bash
make format
```

This runs `ruff format`, `ruff check --fix`, and `mdformat`. You can also
validate JSON and CFF files without modifying them:

```bash
make json-check
make cff-check
```

## Building and checking distributions

Build the source and wheel distributions:

```bash
make package
make check
```

`make check` runs `twine check` on the built artifacts in `dist/`.

## TestPyPI rehearsal

Before a production release, rehearse the release on TestPyPI. Configure
`~/.pypirc` with your TestPyPI API token:

```ini
[testpypi]
username = __token__
password = pypi-<your-testpypi-token>
```

Then run the full rehearsal:

```bash
make release-test
```

This runs `clean`, `test`, `package`, `check`, and `publish-test` (uploads to
TestPyPI). Verify the published package installs from TestPyPI:

```bash
make smoke-test
```

## Pull requests

1. Fork the repository and create a branch from `main`.
1. Make focused changes. Keep commits small and descriptive.
1. Add or update tests for behavioral changes. Include a round-trip assertion
   when changing serialization or parsing.
1. Run `make format` and `make test` before submitting.
1. Update `CHANGELOG.md` under the `## [Unreleased]` section.
1. Open a pull request describing the change and its motivation.

### Model and contract changes

The normative package contract is
[`docs/specs/codemeta-pydantic-v2.md`](docs/specs/codemeta-pydantic-v2.md).
Read it before changing models, parsing, serialization, or migrations.

Do not add typed vocabulary fields without first updating the spec. Known
fields use snake_case Python names and exact JSON-LD aliases. Unknown
properties must survive parse, serialize, and reparse cycles unchanged.

### Tests

Add focused tests for behavioral changes. When changing serialization or
parsing, include a second-parse round-trip assertion that verifies data
survives a `from_jsonld` → `to_jsonld` → `from_jsonld` cycle.

## Versioning

This project follows [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
See [`docs/specs/release-policy.md`](docs/specs/release-policy.md) for the
full versioning policy and release process.

While the major version is `0`, backwards-incompatible changes bump the minor
version. After `1.0.0`, breaking changes require a major version bump.

## Releases

Production releases are published by the GitHub Actions release workflow using
PyPI Trusted Publishing. Do not use `make publish` for production releases.

The release process:

1. Update `version` in `pyproject.toml`.
1. Add a `CHANGELOG.md` entry for the new version.
1. Run `make release-check` to verify the version and changelog.
1. Run `make test` and `make check`.
1. Commit, tag as `vX.Y.Z`, and push.
1. Create a GitHub Release from the tag. The release workflow builds the
   container image and publishes the package to PyPI.

## License

By contributing, you agree that your contributions are licensed under the
[MIT License](LICENSE).
