# AGENTS.md

## Purpose

This repository provides Pydantic v2 models for CodeMeta metadata and JSON-LD.
Keep changes focused on metadata correctness, round-trip safety, and a small
public API.

## Source Of Truth

`docs/specs/codemeta-pydantic-v2.md` is the normative package contract. Read it
before changing models, parsing, serialization, or migrations.

Use the authoritative CodeMeta 3.0, schema.org, JSON-LD 1.1, and RFC 8259
sources linked from the spec only to verify external facts. Do not predict
future vocabulary terms or silently replace package choices recorded in the
spec.

## Invariants

- `from_jsonld()` parses JSON-LD into a validated model without applying legacy migration or normalization.
- Legacy migration and context normalization are explicit operations.
- Known fields use snake_case Python names and exact JSON-LD aliases.
- Unknown properties remain uncoerced raw JSON values.
- Declared context, type, identifier, and unknown null values survive ordinary
  parse, serialize, and reparse cycles.
- Concrete model types are fixed; `CreativeWork` is the documented open
  fallback.
- Do not add typed vocabulary fields without first updating the living spec.

## Workflow

1. Identify the affected normative requirement and model field.
2. Make the smallest implementation change that satisfies it.
3. Add focused tests, including a second-parse round-trip assertion where
   serialization is involved.
4. Run the full suite and package checks.

```bash
uv sync --extra test --group dev
uv run python -m pytest -q -s
uv build
uv run twine check dist/*
```

Keep dependencies minimal. Use contemporary Pydantic v2 APIs and do not add
custom `.dict()`, `.json()`, or `.yaml()` compatibility methods.
