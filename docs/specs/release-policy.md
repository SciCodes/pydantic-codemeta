# Release Policy

## Status

Active. This document governs versioning and release procedures for
`pydantic-codemeta`.

## Versioning

`pydantic-codemeta` follows [Semantic Versioning 2.0.0][semver].

A version number has the form `MAJOR.MINOR.PATCH` with optional
pre-release and build metadata identifiers:

```
MAJOR.MINOR.PATCH[-prerelease][+build]
```

- `MAJOR` increments for incompatible changes to the public API.
- `MINOR` increments for backwards-compatible additions to the public API.
- `PATCH` increments for backwards-compatible fixes that do not change the
  public API.
- Pre-release identifiers (`-alpha`, `-beta`, `-rc`, `-alpha.1`, ...) denote
  unstable releases and sort before the release they modify.
- Build metadata (`+build`, `+sha.abc123`) is ignored for precedence.

[semver]: https://semver.org/spec/v2.0.0.html

## Public API boundary

The public API is the set of names exported through `pydantic_codemeta.__all__`
plus the JSON-LD serialization contracts documented in
[the model specification](./codemeta-pydantic-v2.md).

A change is **breaking** when it does any of the following:

- Removes or renames a name in `__all__`.
- Changes the type, requiredness, or JSON-LD alias of a declared model field.
- Changes the accepted input shape or rejected values for `from_jsonld()`.
- Changes the output of `to_jsonld()` for a model that previously round-tripped.
- Removes or changes the meaning of a `model_config` option that callers rely
  on (for example `extra="allow"` or `populate_by_name`).
- Changes a documented invariant in the model specification.

A change is **backwards-compatible** when it only adds new names, new optional
fields, new accepted input shapes, or fixes behavior to match the documented
contract without narrowing previously accepted input.

## 0.x convention

While the major version is `0`, the public API is not considered stable. During
this period:

- `MINOR` increments mark backwards-compatible additions **and** incompatible
  changes. A breaking change still bumps `MINOR` (not `MAJOR`) until `1.0.0`.
- `PATCH` increments mark backwards-compatible fixes only.
- Callers depending on `0.x` releases should pin an exact version.

The first stable public API is `1.0.0`. After `1.0.0`, the standard SemVer
rules apply in full: breaking changes require a `MAJOR` bump.

## Pre-releases

Pre-release versions use the `MAJOR.MINOR.PATCH-<label>[.<n>]` form with one
of the labels `alpha`, `beta`, or `rc`:

- `0.2.0-alpha.1` — early, incomplete, likely to change.
- `0.2.0-beta.1` — feature-complete pending feedback.
- `0.2.0-rc.1` — release candidate; promoted to `0.2.0` if no defects surface.

Pre-releases are published to TestPyPI first, then PyPI. A pre-release never
becomes `latest` on PyPI until the `-<label>` suffix is dropped.

Use `make release-test` to rehearse a TestPyPI release end-to-end:

```bash
make release-test   # clean, test, package, check, upload to TestPyPI
make smoke-test      # install from TestPyPI and import in an isolated env
```

## Release process

1. Decide the next version following the rules above.
2. Update `version` in `pyproject.toml` to the new version.
3. Add a `CHANGELOG.md` entry under the new version with a release date.
4. Run `make release-check` to verify version consistency and a clean tree.
5. Run `make test` and `make package` and confirm `make check` passes.
6. Commit the version bump and changelog entry.
7. Tag the commit as `vX.Y.Z` (for example `v0.2.0`) and push the tag.
8. Create a GitHub Release from the tag. The release workflow builds the
   container image and publishes the package to PyPI.
9. Confirm the published artifact matches the tag.

`make release` performs steps 6 and 7 after `make release-check` passes.

## Backwards compatibility commitments

Within a major version (or within `0.x` for non-breaking changes), releases
preserve:

- All names in `__all__`.
- The JSON-LD aliases and round-trip behavior of declared fields.
- The behavior of `from_jsonld()`, `to_jsonld()`, `normalize_jsonld_context()`,
  and `migrate_legacy_codemeta()`.
- The documented invariants in the model specification.

A release that needs to break any of these bumps the major version (or the
minor version while `0.x`).
