# AGENTS.md

## Purpose

This repository develops tooling for parsing, validating, manipulating, and converting research software metadata, with a primary focus on CodeMeta and related standards.

Agents should optimize for, in priority order:

1. Correct metadata semantics
2. Standards compliance
3. Long-term maintainability
4. Minimal complexity
5. Backwards-compatible evolution

---

## Before Making Any Substantial Change

Explicitly answer these questions before modifying code:

1. What CodeMeta term(s) are affected?
2. What schema.org type(s) are affected?
3. What JSON-LD behavior changes?
4. How is backwards compatibility affected?
5. What tests demonstrate correctness?

If any of these cannot be answered clearly, continue analysis before proceeding.

---

## Repository Philosophy

The information model is more important than implementation details.

When making design decisions:

* Prefer clarity over cleverness
* Prefer explicit typing over dynamic behavior
* Prefer standards compliance over convenience
* Prefer stable APIs over short-term shortcuts

---

## Current Architecture

Target package:

```text
src/codemeta_datamodel/
```

This layer provides:

* A typed in-memory representation of CodeMeta metadata
* JSON-LD serialization and deserialization
* Validation using Pydantic v2
* A foundation for metadata conversion workflows

Non-goals:

* Complete schema.org coverage
* Automatic generation of all schema.org types
* General-purpose RDF tooling

---

## Source of Truth

The canonical CodeMeta vocabulary is at:

```text
https://w3id.org/codemeta/3.0
```

If repository documentation conflicts with the canonical vocabulary, treat the vocabulary as authoritative and update the documentation.

Do not invent CodeMeta terms. Do not silently rename CodeMeta properties.

---

## Versioning

CodeMeta versioning is a first-class architectural concern.

The canonical vocabulary source is currently:

```text
https://w3id.org/codemeta/3.0
```

However, the project expects to adopt CodeMeta v4 when it becomes available and stable.

### Current Policy

* The default serialization target is currently CodeMeta 3.0.
* New model design should anticipate eventual CodeMeta v4 support.
* Avoid assumptions that vocabulary structure, term availability, or required properties are fixed to a single CodeMeta release.

### Context Handling

The `@context` URI is meaningful and identifies the vocabulary version.

Implementations shall:

* Preserve the declared `@context` value during round-trip serialization.
* Never silently upgrade or downgrade the declared version.
* Only perform version migrations when explicitly requested by the caller.

### Version-Aware Design

When version-specific behavior becomes necessary:

* Encapsulate it behind a version identifier.
* Centralize vocabulary differences.
* Avoid scattering version conditionals throughout model implementations.

Good:

```python
version = CodeMetaVersion.V3
```

Bad:

```python
if context == "https://w3id.org/codemeta/3.0":
    ...
```

throughout the codebase.

### Vocabulary Evolution

Agents should assume that:

* New terms may appear in future CodeMeta releases.
* Existing terms may become deprecated.
* Additional schema.org types may become relevant.

Model implementations should therefore favor extension over rigid enumeration whenever practical.

### Testing Requirements for Versioning

Version-aware behavior must include tests covering:

* Context preservation
* Serialization fidelity
* Migration behavior (if implemented)
* Backwards compatibility for supported versions

---

## Modeling Guidelines

### Prefer Explicit Types

```python
# Good
author: Person | Organization | Role | str | None

# Bad
author: Any
```

Avoid untyped containers.

### Field Naming and Aliases

CodeMeta properties use camelCase. Python model fields use snake_case.

Use Pydantic field aliases to bridge them:

```python
class SoftwareSourceCode(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    software_version: str | None = Field(None, alias="softwareVersion")
    code_repository: AnyUrl | None = Field(None, alias="codeRepository")
```

All aliases must correspond to actual CodeMeta or schema.org property names. Do not invent aliases.

### Preserve Unknown Properties

Unknown metadata fields must survive round-trip serialization. Use Pydantic's `extra='allow'` to store them as raw JSON-compatible values:

```python
model_config = ConfigDict(extra="allow", populate_by_name=True)
```

Do not attempt dynamic type inference on unknown fields. Preserve them as received.

### JSON-LD Compatibility

Always preserve `@context`, `@type`, and `@id` through the serialization lifecycle.

`@type` must always be present in serialized output for concrete types.

When serializing, emit `@context` exactly as received unless a version migration was explicitly requested.

### Dates

Accept ISO date strings and `datetime.date` objects.

* Parse valid ISO dates into `date`
* Preserve unparseable values as strings rather than raising

### Error Handling

Validation errors should be specific and actionable. Distinguish between:

* **Invalid structure**: a field is present but has the wrong type or shape (raise `ValidationError`)
* **Unrecognized terms**: unknown properties that should be preserved (store, do not raise)
* **Unparseable values**: values that cannot be coerced to the target type (preserve as string with a warning, where the schema permits it)

Never silently discard metadata. If a value cannot be modeled, preserve it.

---

## Pydantic Guidance

Target Pydantic v2. Use contemporary APIs throughout.

Do not introduce `pydantic.v1` dependencies. Design models so future Pydantic upgrades remain manageable — avoid deep coupling to framework internals.

---

## Testing Requirements

Every change must include tests. At minimum verify:

* Parsing
* Validation
* Serialization
* Round-trip behavior

```python
model = CodeMeta.from_jsonld(data)
serialized = model.to_jsonld()
assert semantic_equivalence(data, serialized)
```

For metadata models also test:

* Field aliases (camelCase ↔ snake_case)
* Nested objects
* JSON-LD serialization (`@context`, `@type`, `@id` preservation)
* Unknown property preservation
* Date handling (ISO strings, `date` objects, unparseable values)
* Version-specific behavior when applicable

Prefer fixture-driven tests for metadata records.

---

## Dependency Policy

Before introducing a new dependency, ask:

1. Can the standard library solve this?
2. Can an existing dependency solve this?
3. Is the dependency actively maintained?
4. Does it materially reduce complexity?

Prefer fewer dependencies. Avoid dependencies that merely wrap simple functionality.

---

## Documentation Requirements

When introducing new metadata terms, model types, or conversion behavior, update documentation in the same change.

Documentation should explain:

* Why a type exists
* How it relates to CodeMeta
* Any important interoperability or versioning concerns

---

## Agent Workflow

### 1. Understand the Information Model

Before writing code, identify:

* Relevant CodeMeta terms and their canonical definitions
* schema.org types involved
* Required serialization behavior
* Whether versioning affects the terms in scope

### 2. Minimize Scope

Implement the smallest change that satisfies requirements. Avoid speculative abstractions and types that are not currently needed.

### 3. Add Tests

Every behavioral change must have tests. Prefer fixtures over procedural setup.

### 4. Verify Round-Trip Behavior

Round-trip integrity is a core project requirement. Confirm that `from_jsonld → to_jsonld` preserves all metadata semantics, including unknown properties and the declared `@context` version.

### 5. Update Documentation

If behavior changes, documentation must change in the same PR.

---

## Pull Request Expectations

A good PR solves one problem, includes tests, and updates documentation when needed.

Do not mix into a single PR:

* Architectural changes
* Dependency upgrades
* Formatting-only changes
* Metadata model changes

---

## Definition of Done

A change is complete when:

* Implementation is correct
* Tests pass
* Documentation is updated
* CodeMeta semantics are preserved
* JSON-LD round-trip behavior is verified, including `@context` version fidelity
* No unnecessary dependencies were introduced