# Changelog

All notable changes to `pydantic-codemeta` are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html).
See [the release policy](docs/specs/release-policy.md) for the full versioning
rules and release process.

## [Unreleased]

## [0.1.0] - 2026-09-09

### Added

- Pydantic v2 models for CodeMeta 3.0 and schema.org vocabulary terms.
- `CodeMeta`, `CodeMetaV3`, `SoftwareSourceCode`, `SoftwareApplication`, and
  supporting schema.org models (`Person`, `Organization`, `CreativeWork`, ...).
- `from_jsonld()` and `to_jsonld()` for JSON-LD parsing and serialization.
- `normalize_jsonld_context()` and `migrate_legacy_codemeta()` for explicit
  context normalization and legacy migration.
- `CITATION.cff` and `codemeta.json` metadata.
- Docker-based test and packaging workflows.
- `make format` target to format Python and Markdown with `ruff` and `mdformat`.
- `make json-check` and `make json-format` targets to validate and canonicalize
  JSON files with `python -m json.tool`.
- `make cff-check` (with `make cff-validate` alias) target to validate
  `CITATION.cff` with the `ghcr.io/scicodes/cffconvert:v2026.08` container image.
- Dev dependencies for formatting: `ruff`, `mdformat`, `mdformat-gfm`,
  `mdformat-frontmatter`.
- Release policy governing Semantic Versioning 2.0.0 and the release process.
