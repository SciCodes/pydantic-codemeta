# CodeMeta Schema.org Model Layer Specification

## Status

Draft

## Motivation

`codemeticulous` currently depends on a schema.org model layer that is implemented using `pydantic.v1.BaseModel`. This creates an inconsistency within the codebase because the remainder of the project uses Pydantic v2.

The goal of this specification is to define a clean-room, Pydantic v2-native implementation of the schema.org types required to support CodeMeta metadata validation, serialization, and conversion workflows.

This implementation is intentionally scoped to the CodeMeta vocabulary and is not intended to provide complete coverage of the schema.org ecosystem.

## Goals

### Primary Goals

* Eliminate all runtime dependence on `pydantic.v1`.
* Provide a fully Pydantic v2-native schema.org model layer.
* Support parsing and serialization of CodeMeta JSON-LD documents.
* Support the complete set of terms defined by the current CodeMeta vocabulary.
* Preserve unknown properties for forward compatibility with future CodeMeta and schema.org extensions.
* Provide a foundation that can be incrementally extended as additional schema.org types become necessary.

### Non-Goals

* Complete schema.org coverage.
* Automatic generation of all schema.org types.
* Backward compatibility with the internal implementation details of external schema.org libraries.
* Exact replication of inheritance hierarchies from existing implementations.

## Future Compatibility

This work is being structured with the expectation that CodeMeta v4 will become the next target vocabulary version soon.

The implementation should therefore favor clean extensibility over assumptions tied exclusively to the current CodeMeta release.

## Design Principles

### Pydantic v2 Native

All models shall use Pydantic v2 APIs exclusively.

No imports from `pydantic.v1` are permitted.

### JSON-LD First

The model layer shall support direct parsing and serialization of JSON-LD structures, including support for:

* `@context`
* `@type`
* `@id`

Serialization shall produce schema.org-compatible field names using aliases.

### Explicit Typing

Relations shall be represented using explicit unions of supported node types rather than untyped containers.

Examples:

```python
AuthorType = Person | Organization | Role | str
AuthorField = AuthorType | list[AuthorType]
```

### Forward Compatibility

Models shall permit unknown properties and preserve them during round-trip serialization.

This is necessary because CodeMeta documents frequently contain community-specific extensions and schema.org evolves independently of CodeMeta releases.

### Extensibility

The model hierarchy should make it straightforward to add additional schema.org types in future releases without requiring substantial refactoring.

## Supported Types

The implementation shall provide the following schema.org types:

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

Additionally, the implementation shall provide:

* SchemaOrgBase (abstract base model)
* CodeMeta (convenience wrapper around `SoftwareSourceCode`)

## CodeMeta Wrapper

`CodeMeta` is not a distinct schema.org type.

Instead, it represents a specialized `SoftwareSourceCode` model with default JSON-LD metadata corresponding to the current CodeMeta context.

Default serialization shall include:

```json
{
  "@context": "https://w3id.org/codemeta/3.0",
  "@type": "SoftwareSourceCode"
}
```

## CodeMeta Vocabulary

The implementation shall target the CodeMeta vocabulary as defined by the canonical CodeMeta source.

Canonical source:

https://w3id.org/codemeta/3.0

The term lists and examples contained in this specification are informational only.

If there is any conflict between this document and the canonical CodeMeta source, the canonical source shall take precedence.

## Vocabulary Coverage

The implementation shall support the complete vocabulary defined by the canonical CodeMeta source.

The following categories are expected to be represented:

### Schema.org Software Terms

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

### Schema.org Person, Thing, Role, and Review Terms

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

Where role-aware relationships are supported, the accepted union type shall be:

```python
Person | Organization | Role | str
```

This applies to fields such as:

* author
* contributor
* maintainer

and any similar contributor-style relationships defined by CodeMeta.

## Tricky Field Type Mappings

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

## Date Parsing and Serialization

Date fields shall accept both ISO date strings and native `datetime.date` objects.

Parsing preference:

* If the input is a parseable ISO 8601 date string, coerce it to `datetime.date`.
* If the input is not parseable as a date, preserve it as `str`.

This allows consumers to reliably compare valid dates while remaining tolerant of real-world metadata that uses nonstandard date formats.

## Validation Requirements

The model layer shall:

* Validate known field types.
* Accept nested schema.org objects where appropriate.
* Accept JSON-LD aliases directly.
* Accept both Python field names and alias names during construction.
* Preserve unknown properties.
* Support date values represented either as strings or native date objects.

Validation should remain pragmatic rather than unnecessarily restrictive in order to support real-world metadata records.

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

1. No runtime dependency on `pydantic.v1` remains.
2. CodeMeta documents can be parsed into strongly typed Pydantic v2 models.
3. CodeMeta documents can be serialized back to valid JSON-LD.
4. Unknown properties survive round-trip serialization.
5. The complete CodeMeta vocabulary is represented by the model layer.
6. Existing CodeMeta functionality continues to operate using the new models.
7. The implementation is covered by automated tests.
8. The design remains extensible for future CodeMeta vocabulary revisions, including CodeMeta v4.
