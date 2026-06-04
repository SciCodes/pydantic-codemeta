# CodeMeta Data Model Specification

## Status

Draft

## Motivation

The goal of this specification is to define a typed, maintainable model layer for in-memory CodeMeta metadata handling.

The implementation should support parsing, validation, manipulation, and serialization of CodeMeta metadata while remaining aligned with the CodeMeta vocabulary and JSON-LD representation.

The current implementation target is Pydantic v2. The model layer should be structured so that future Pydantic upgrades can be accommodated with minimal disruption.

This implementation is intentionally scoped to CodeMeta metadata handling and is not intended to provide complete schema.org coverage.

## Scope

### In Scope

* Typed models for the CodeMeta vocabulary used by `codemeticulous`
* JSON-LD parsing and serialization
* Preservation of unknown properties
* Round-trip-friendly model behavior
* Support for CodeMeta-specific terms and schema.org terms used by CodeMeta
* Practical in-memory editing of metadata records
* Validation of CodeMeta records using contemporary Pydantic APIs

### Out of Scope

* Complete schema.org coverage
* Automatic generation of all schema.org types
* Standalone package extraction
* Recreation of external schema.org model implementations
* Exact replication of inheritance hierarchies from existing libraries

## Packaging and Source Tree

The implementation shall live under:

```text
src/codemeta_pydantic/
```

This package is an internal implementation detail of `codemeticulous` intended to provide convenient typed data models for in-memory CodeMeta work.

Although the current implementation target is Pydantic v2, the architecture should remain focused on the CodeMeta information model rather than framework-specific implementation details.

The source tree should be organized so the model layer remains easy to maintain and can be extracted later if needed, but standalone extraction is explicitly out of scope for this work.

## Future Compatibility

This work is being structured with the expectation that CodeMeta will continue to evolve, including future CodeMeta v4 changes.

The implementation should favor clean extensibility and practical metadata handling over assumptions tied exclusively to the current CodeMeta release.

## Design Principles

### Modern Pydantic

The implementation shall target the current supported Pydantic release series.

At the time of writing, the target is Pydantic v2.

The implementation should use contemporary Pydantic APIs and idioms and avoid unnecessary coupling to framework internals that would make future upgrades difficult.

### JSON-LD First

The model layer shall support direct parsing and serialization of JSON-LD structures, including support for:

* `@context`
* `@type`
* `@id`

Serialization shall produce schema.org-compatible field names using aliases.

### Explicit Typing

Relations shall be represented using explicit unions of supported node types rather than untyped containers.

Example:

```python
AuthorType = Person | Organization | Role | str
AuthorField = AuthorType | list[AuthorType]
```

### Forward Compatibility

Models shall permit unknown properties and preserve them during round-trip serialization.

Unknown properties shall be stored and round-tripped as raw JSON-compatible values without additional type inference, coercion, or interpretation.

Implementations should not attempt to dynamically construct typed objects from unknown properties.

This behavior is required to preserve forward compatibility with future CodeMeta releases, community extensions, and schema.org evolution.

### Extensibility

The model hierarchy should make it straightforward to add additional CodeMeta vocabulary terms and supporting types in future releases without requiring substantial refactoring.

## Supported Types

The implementation shall provide the following types:

### Core Types

* Thing
* Person
* Organization
* ContactPoint
* PostalAddress
* PropertyValue
* CreativeWork
* MediaObject
* DataFeed
* Review
* Role
* ComputerLanguage
* ScholarlyArticle
* SoftwareSourceCode
* SoftwareApplication

### Infrastructure Types

* SchemaOrgBase
* CodeMeta

### Supporting Type Rationale

The following supporting types are included because they are referenced by the CodeMeta vocabulary and related schema.org terms:

| Type               | Purpose                                                                        |
| ------------------ | ------------------------------------------------------------------------------ |
| `PostalAddress`    | Supports structured `Person.address` values.                                   |
| `MediaObject`      | Supports `encoding` and related media representations.                         |
| `DataFeed`         | Supports `supportingData`.                                                     |
| `ScholarlyArticle` | Supports `referencePublication`.                                               |
| `ComputerLanguage` | Supports structured `programmingLanguage` values.                              |
| `Role`             | Supports contributor role modeling via `roleName`, `startDate`, and `endDate`. |

These types are included to support CodeMeta use cases and are not intended to provide complete schema.org coverage.

## CodeMeta Model

`CodeMeta` is a convenience model for in-memory manipulation of CodeMeta metadata.

It is not intended to be a general-purpose schema.org implementation.

Default serialization shall include:

```json
{
  "@context": "https://w3id.org/codemeta/3.0",
  "@type": "SoftwareSourceCode"
}
```

## Vocabulary Source of Truth

The implementation shall target the CodeMeta vocabulary as defined by the canonical CodeMeta source:

https://w3id.org/codemeta/3.0

Examples, mappings, and term lists in this specification are informational only.

If there is any conflict between this document and the canonical CodeMeta source, the canonical source takes precedence.

The implementation should be designed so that future CodeMeta vocabulary releases, including CodeMeta v4, can be adopted without major architectural changes.

## Vocabulary Coverage

The implementation shall support the CodeMeta vocabulary required for in-memory metadata handling within `codemeticulous`.

Coverage includes, but is not limited to, the following categories.

### Software Metadata Terms

Examples include:

* author
* contributor
* maintainer
* publisher
* provider
* producer
* funder
* sponsor
* citation
* review
* programmingLanguage
* softwareRequirements
* supportingData
* identifier
* keywords
* license
* version
* dateCreated
* dateModified
* datePublished
* codeRepository
* downloadUrl
* installUrl
* runtimePlatform
* operatingSystem
* memoryRequirements
* processorRequirements
* storageRequirements
* softwareHelp
* targetProduct
* relatedLink
* sameAs

### Person, Organization, Role, and Review Terms

Examples include:

* affiliation
* contactPoint
* address
* reviewBody
* reviewAspect
* roleName
* startDate
* endDate

### CodeMeta-Specific Terms

Examples include:

* buildInstructions
* contIntegration
* continuousIntegration
* developmentStatus
* embargoDate
* embargoEndDate
* funding
* hasSourceCode
* isSourceCodeOf
* issueTracker
* readme
* referencePublication
* softwareSuggestions

The canonical CodeMeta vocabulary remains authoritative.

## Role Modeling

`schema:Role` is used by CodeMeta to associate a person or organization with a role description and optional date range.

The implementation shall support:

* `roleName`
* `startDate`
* `endDate`

Role-aware relationships shall support:

```python
Person | Organization | Role | str
```

This applies to fields such as:

* author
* contributor
* maintainer

and similar contributor-style relationships.

## Normative Field Type Mappings

The following mappings are normative.

| Field                 | Accepted Type                                                      |
| --------------------- | ------------------------------------------------------------------ |
| `programmingLanguage` | `ComputerLanguage \| str \| list[ComputerLanguage \| str] \| None` |
| `license`             | `CreativeWork \| str \| None`                                      |
| `identifier`          | `str \| PropertyValue \| list[str \| PropertyValue] \| None`       |
| `citation`            | `CreativeWork \| str \| None`                                      |
| `author`              | `Person \| Organization \| Role \| str \| list[...] \| None`       |
| `contributor`         | `Person \| Organization \| Role \| str \| list[...] \| None`       |
| `maintainer`          | `Person \| Organization \| Role \| str \| list[...] \| None`       |

## Serialization Contract

The canonical serialization format shall be:

```python
model.model_dump(
    by_alias=True,
    exclude_none=True,
    mode="json",
)
```

All models shall expose convenience helpers for JSON-LD serialization and deserialization.

Round-trip serialization shall preserve:

* aliases
* nested objects
* lists
* unknown properties

### `@type` Serialization Requirement

All concrete model types shall define a non-null `@type` value.

`@type` shall always be serialized on concrete types and shall never be omitted from serialized output.

Implementations shall not model `@type` as an optional field on concrete classes.

This requirement exists to ensure valid JSON-LD output and reliable type discrimination during parsing and serialization.

## Date Parsing and Serialization

Date fields shall accept both ISO date strings and native `datetime.date` objects.

Parsing preference:

* If the input is a parseable ISO 8601 date string, coerce it to `datetime.date`.
* If the input is not parseable as a date, preserve it as `str`.

This allows consumers to compare valid dates while remaining tolerant of real-world metadata that uses nonstandard date formats.

## Validation Requirements

The model layer shall:

* Validate known field types.
* Accept nested objects where appropriate.
* Accept JSON-LD aliases directly.
* Accept both Python field names and alias names during construction.
* Preserve unknown properties.
* Support date values represented either as strings or native date objects.

Validation should remain pragmatic rather than unnecessarily restrictive.

## Testing Requirements

The implementation shall include fixture-based tests covering:

### Model Behavior

* Alias handling
* Nested object parsing
* JSON-LD round-trip serialization
* Preservation of `@type`
* Preservation of unknown properties
* Validation failures for clearly invalid inputs

### CodeMeta Documents

Tests shall include representative CodeMeta documents demonstrating:

* Multiple authors
* Nested organizations
* Structured identifiers via `PropertyValue`
* Role-based authorship
* Date fields
* Reviews
* CodeMeta-specific properties
* Unknown extension properties

Round-trip serialization of these fixtures shall preserve semantic content.

## Acceptance Criteria

This work is complete when:

1. CodeMeta documents can be represented as typed models for in-memory use.
2. The implementation targets the current supported Pydantic release series (currently Pydantic v2).
3. CodeMeta documents can be serialized back to valid JSON-LD.
4. Unknown properties survive round-trip serialization.
5. The required CodeMeta vocabulary is represented by the model layer.
6. All pre-existing tests in the `tests/` suite pass without modification.
7. The implementation is covered by automated tests.
8. The design remains extensible for future CodeMeta vocabulary revisions, including CodeMeta v4.
