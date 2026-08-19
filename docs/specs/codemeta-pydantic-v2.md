# CodeMeta Data Model Specification

## Status

Draft. This document defines the required behavior of the Pydantic v2 model
layer in `src/pydantic_codemeta/`.

## Purpose

The package provides typed Python models for CodeMeta metadata. It validates
known fields, preserves unfamiliar metadata, and serializes models as JSON-LD.
It is not a complete schema.org implementation or a closed CodeMeta
validator.

The design must support later CodeMeta releases without replacing the parser,
serializer, extra-property handling, or basic class hierarchy.

## Normative Language and Sources

`Must` and `must not` state requirements. `May` states permitted behavior.

The following external sources define facts used by this specification:

- [CodeMeta 3.0 terms](https://w3id.org/codemeta/3.0) define the current
  property names and value ranges.
- [The schema.org data model](https://schema.org/docs/datamodel.html) states
  that properties may have multiple values and that JSON-LD represents those
  values as arrays.
- [JSON-LD 1.1](https://www.w3.org/TR/json-ld11/) defines the permitted
  `@context` shapes and JSON-LD keywords.
- [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) defines JSON values and
  excludes `NaN` and infinity from JSON numbers.

CodeMeta and schema.org define vocabulary semantics. This document separately
defines package choices such as Python unions, accepted scalar/list forms,
and tolerant string references. Those package choices are normative for this
library even when they are broader than a vocabulary range.

No requirement in this document predicts CodeMeta v4 terms.

## Scope

The package must provide:

- typed models for the inventory in this document;
- Pydantic v2 validation;
- JSON-LD parsing and serialization;
- Python field names and JSON-LD aliases;
- typed nested objects for known terms;
- recursive preservation of unknown JSON-compatible values;
- explicit normalization and legacy migration helpers; and
- semantic round trips through parse, serialize, and reparse.

The package does not provide:

- complete schema.org coverage;
- general RDF processing or reasoning;
- remote context loading;
- dynamic model generation from `@type` or `@context`;
- automatic vocabulary-version migration during parsing; or
- lexical or byte-for-byte JSON preservation.

## Architecture

The class relationship is:

```text
SchemaOrgBase
    |
  Thing
    |
CreativeWork
    |
SoftwareSourceCode
    |
 CodeMeta
    |
CodeMetaV3
```

`SchemaOrgBase` provides common validation, aliases, extra-property storage,
and JSON-LD helpers. `Thing`, `CreativeWork`, and `SoftwareSourceCode` are
stable information-model classes. They are not tied to one CodeMeta release.

`CodeMeta` is the open document model. It defaults to the CodeMeta 3.0 context
but accepts other supported context values. `CodeMetaV3` specializes
`CodeMeta` by requiring the CodeMeta 3.0 context.

Other concrete schema.org classes may inherit from `Thing` or `CreativeWork`
where that relationship is semantically correct. Python inheritance need not
copy the complete schema.org hierarchy.

A version binding constrains version-specific behavior. It must not reject an
unknown property merely because that property is absent from the known
version's typed inventory.

## Required Model Types

The public model inventory is:

- `SchemaOrgBase`
- `Thing`
- `PropertyValue`
- `ContactPoint`
- `PostalAddress`
- `Organization`
- `Person`
- `Role`
- `ComputerLanguage`
- `CreativeWork`
- `MediaObject`
- `DataFeed`
- `Review`
- `ScholarlyArticle`
- `SoftwareSourceCode`
- `SoftwareApplication`
- `CodeMeta`
- `CodeMetaV3`

`VersionedLanguage` is not a CodeMeta or schema.org type and must not be part
of this inventory. An unfamiliar property such as `version` on a
`ComputerLanguage` remains available as a raw extra.

## Typed and Open Coverage

A property has typed coverage only when a declared Pydantic field validates
it. A property has open coverage when it is retained as a raw extra. Open
coverage does not imply a typed field.

The following table is the complete required typed-field inventory for this
version. Names in the table are JSON-LD aliases. Each model also inherits the
fields of its parent. A field not listed here is not part of the canonical
typed API, even if it is valid CodeMeta, schema.org, or extension metadata.
Such a field must still round-trip as an extra.

Adding another first-class field changes the typed API and requires a
specification update.

| Model                 | Fields introduced by that model                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `SchemaOrgBase`       | `@id`, `@type`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `Thing`               | `name`, `description`, `url`, `identifier`, `relatedLink`, `sameAs`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `PropertyValue`       | `value`, `propertyID`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| `ContactPoint`        | `contactType`, `email`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `PostalAddress`       | `streetAddress`, `addressLocality`, `addressRegion`, `postalCode`, `addressCountry`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `Organization`        | `email`, `contactPoint`, `address`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `Person`              | `email`, `givenName`, `familyName`, `affiliation`, `contactPoint`, `address`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `Role`                | `roleName`, `startDate`, `endDate`, `author`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `ComputerLanguage`    | no fields beyond `Thing`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `CreativeWork`        | `author`, `contributor`, `editor`, `publisher`, `copyrightHolder`, `copyrightYear`, `funder`, `sponsor`, `provider`, `producer`, `license`, `citation`, `review`, `isPartOf`, `hasPart`, `encoding`, `keywords`, `position`, `dateCreated`, `dateModified`, `datePublished`                                                                                                                                                                                                                                                                                                                                                                                      |
| `MediaObject`         | `contentUrl`, `encodingFormat`, `contentSize`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `DataFeed`            | `dataFeedElement`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `Review`              | `reviewBody`, `reviewAspect`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `ScholarlyArticle`    | no fields beyond `CreativeWork`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `SoftwareSourceCode`  | `@context`, `codeRepository`, `programmingLanguage`, `runtimePlatform`, `targetProduct`, `applicationCategory`, `applicationSubCategory`, `downloadUrl`, `fileSize`, `installUrl`, `memoryRequirements`, `operatingSystem`, `permissions`, `processorRequirements`, `releaseNotes`, `softwareHelp`, `softwareRequirements`, `softwareVersion`, `storageRequirements`, `fileFormat`, `isAccessibleForFree`, `version`, `supportingData`, `maintainer`, `buildInstructions`, `continuousIntegration`, `developmentStatus`, `embargoEndDate`, `funding`, `hasSourceCode`, `isSourceCodeOf`, `issueTracker`, `readme`, `referencePublication`, `softwareSuggestions` |
| `SoftwareApplication` | `applicationCategory`, `applicationSubCategory`, `operatingSystem`, `softwareVersion`, `downloadUrl`, `installUrl`, `memoryRequirements`, `processorRequirements`, `storageRequirements`, `permissions`, `supportingData`                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `CodeMeta`            | no new vocabulary fields; supplies the open context default                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `CodeMetaV3`          | no new vocabulary fields; constrains the context to CodeMeta 3.0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

Every listed field must have an explicit type. `Any` is not permitted for a
known field. Its scalar value types must follow the CodeMeta 3.0 range or the
relevant schema.org range. Text, URL, compact IRI, and other string references
use `str` unless this document names a structured model. The package may use
unions with `str` to retain practical references that cannot be resolved
locally.

The cardinalities and unions in the normative mapping table below take
precedence over a narrower first-pass implementation.

### Legacy Property Names

The following names are not typed fields:

- `creator`
- `contIntegration`
- `embargoDate`

`from_jsonld()` preserves them as extras. Explicit legacy migration renames
them as follows:

- `creator` to `author`
- `contIntegration` to `continuousIntegration`
- `embargoDate` to `embargoEndDate`

The canonical and legacy names may coexist during ordinary parsing. Migration
must reject an input containing both names in one pair.

## Python Names and JSON-LD Aliases

Python fields use snake_case. JSON-LD serialization uses the exact aliases in
the typed inventory. Examples include:

```text
code_repository        <-> codeRepository
continuous_integration <-> continuousIntegration
property_id            <-> propertyID
context                <-> @context
type                   <-> @type
id                     <-> @id
```

Construction may use a Python name or its alias. One input must not contain
both forms for the same field. Collision detection is based on key presence,
before value validation. It does not depend on truthiness or equality.

Both of these inputs must fail:

```python
{"code_repository": None, "codeRepository": None}
{"code_repository": "x", "codeRepository": "x"}
```

This rule also applies to `id` and `@id`, `type` and `@type`, and `context`
and `@context`.

An unknown property whose name matches a Python method, such as `model_dump`,
remains in `model_extra` and must serialize under its original name.

## Raw JSON Values

Unknown properties must already contain raw JSON-compatible values. The
package must not coerce an unknown value into JSON-compatible data.

The recursive definition is:

```text
JSONValue =
    null
    | boolean
    | integer
    | finite floating-point number
    | string
    | array of JSONValue
    | object with string keys and JSONValue values
```

Validation applies at every nesting depth. Therefore:

- `NaN`, positive infinity, and negative infinity are rejected;
- tuples are not converted to arrays and are rejected;
- sets are rejected;
- `datetime.date` and `datetime.datetime` are rejected as unknown values;
- arbitrary Python objects are rejected;
- arbitrary Pydantic models are rejected; and
- a dictionary with any non-string key is rejected.

Known fields still perform their documented type validation and conversion.
These raw-value rules apply only to unknown properties and raw context-object
contents.

Unknown JSON-LD keywords, prefixed properties, scalars, arrays, and nested
objects follow the same rule. The package must not infer a Pydantic model from
an unknown object's `@type`.

## JSON-LD Keywords

### `@context`

The package uses these conceptual types:

```python
JSONValue = (
    None | bool | int | finite_float | str | list[JSONValue] | dict[str, JSONValue]
)
ContextObject = dict[str, JSONValue]
ContextEntry = str | ContextObject | None
Context = ContextEntry | list[ContextEntry]
```

`finite_float` means a Python `float` for which `math.isfinite(value)` is
true. The aliases above describe recursive types; an implementation may use
equivalent Pydantic-compatible aliases.

A context array may be empty. It may contain strings, context objects, and
null entries in any combination. It must not contain another array.

`from_jsonld()` must preserve whether the context was a string, object, array,
or null. It must preserve context-array order and null entries. The package
performs structural validation only: it does not fetch a remote context or
fully validate context term definitions.

For `CodeMeta`:

- an omitted `@context` uses `https://w3id.org/codemeta/3.0`;
- an explicitly supplied `@context: null` remains null and serializes as
  `"@context": null`; and
- another structurally valid context is preserved without an implicit upgrade
  or downgrade.

`CodeMetaV3` accepts only the literal CodeMeta 3.0 context. Converting an open
`CodeMeta` model to `CodeMetaV3` must reject another string context, a context
object, or a context array. An absent or null context may be replaced with the
v3 context only during an explicit v3 conversion.

### `@type`

Every concrete model must emit its correct, non-null `@type`. A caller must
not replace a concrete class's type. Concrete classes use `Literal[...]` or an
equivalent constraint.

Typed models in this package accept one string `@type`, not an array. JSON-LD
permits multi-valued `@type`, but supporting it is outside this typed model
layer. A multi-valued type may still occur inside a raw unknown property.

`CreativeWork` is the documented open fallback described below.

### `@id`

`@id` is an optional string. Parsing and serialization must preserve it. Its
behavior does not depend on the CodeMeta version.

## `CreativeWork` Fallback

`CreativeWork` serves two purposes: it is the parent of known creative-work
models, and it is the fallback for an unfamiliar creative-work subtype in a
field that accepts `CreativeWork`.

For example, this value may be parsed as `CreativeWork`:

```json
{
  "@type": "Dataset",
  "name": "example"
}
```

The parsed model's `type` must be `"Dataset"`. `to_jsonld()` must emit
`"@type": "Dataset"`, and reparsing must produce equivalent model state. The
fallback must not replace the supplied type with `"CreativeWork"`.

If the input omits `@type`, a fallback `CreativeWork` may use
`"CreativeWork"` as its default type.

When a relationship union contains a more specific implemented class and the
input type matches it, the parser should use that class. Otherwise it may use
the `CreativeWork` fallback unless the type is known to be incompatible.

A type is known to be incompatible when it names an implemented concrete
class that does not inherit from `CreativeWork`. Examples include `Person`,
`Organization`, `Role`, `ContactPoint`, `PostalAddress`, `PropertyValue`, and
`ComputerLanguage`. Such a value must be rejected in a CreativeWork-only
field.

An unfamiliar type that is not in the package's model inventory may use the
fallback. The package does not perform schema.org subclass lookup or general
RDF reasoning, so it must not claim that the unknown type is semantically a
CreativeWork. It only preserves the node in a field whose contract permits
the fallback.

No dynamic type registry is required.

## Normative Relationship Types and Cardinalities

CodeMeta 3.0 and schema.org define value ranges. Schema.org also permits any
property to have multiple values. The following scalar/list policy is a
package design choice for tolerant in-memory metadata handling.

Each field in this table accepts its scalar form, its repeated form, or
`None`. A repeated form is one flat list whose elements each match the scalar
type. Nested lists are invalid. Scalar input remains scalar after parsing;
list input remains a list.

```python
Agent = Person | Organization | Role | str
```

| Field                 | Scalar form        | Repeated form |
| --------------------- | ------------------ | ------------- |
| `programmingLanguage` | \`ComputerLanguage | str\`         |
| `license`             | \`CreativeWork     | str\`         |
| `identifier`          | \`PropertyValue    | str\`         |
| `citation`            | \`CreativeWork     | str\`         |
| `author`              | `Agent`            | `list[Agent]` |
| `contributor`         | `Agent`            | `list[Agent]` |
| `maintainer`          | `Agent`            | `list[Agent]` |

The external vocabulary ranges are narrower in two relevant ways:

- CodeMeta lists `Organization | Person` for `author` and `contributor`, and
  `Person` for `maintainer`.
- CodeMeta uses `CreativeWork | URL` for `license` and `citation`,
  `ComputerLanguage | Text` for `programmingLanguage`, and
  `PropertyValue | URL` for `identifier`.

Accepting `Role` in contributor-style fields and accepting `str` for text,
URLs, compact IRIs, or unresolved references are package choices. They do not
change the CodeMeta vocabulary ranges.

Plain JSON arrays represent repeated values. Their RDF meaning is unordered
unless the document uses explicit JSON-LD list semantics. This package
preserves input array order but does not add `@list` automatically.

## Date Values

Known date fields accept `datetime.date` or `str`.

- A valid ISO date string is converted to `datetime.date`.
- A non-date string is retained as `str`.
- An ISO datetime string remains a string; it is not truncated to a date.
- A native `datetime.datetime` is rejected.
- Other input types are rejected.

Serialization emits a parsed `datetime.date` as an ISO date string. This
conversion is intentional and does not require lexical round-trip identity.

## Parsing and Explicit Transforms

### Ordinary Parsing

`from_jsonld()` validates the input without changing property names or
context. It must not:

- normalize a context;
- flatten prefixed keys;
- rename legacy properties;
- add a migration; or
- upgrade or downgrade a vocabulary version.

Known fields become typed values. Unknown fields remain raw JSON values.

### Context Normalization

`normalize_jsonld_context()` is an explicit, root-only representation
transform. It is a small compatibility helper, not a JSON-LD expansion
algorithm.

If `@context` is not an object, the helper returns a shallow copy without
changing the context or any property name. For a context object:

1. Each non-keyword context key is treated as a configured prefix. A keyword
   starts with `@` and is not a prefix.
1. For each root property named `prefix:localName`, if `prefix` is configured,
   the helper renames that property to `localName`.
1. If `localName` is already present at the root, the helper raises an error.
   Collision checks use key presence, not values.
1. Root properties with an unconfigured prefix remain unchanged.
1. The helper removes the context object after processing, even when no root
   property used a configured prefix.
1. The helper does not inspect or change nested objects.

This operation is intentionally lossy and is outside the ordinary round-trip
guarantee.

### Legacy Migration

`migrate_legacy_codemeta()` is an explicit, root-only property rename. It uses
the three mappings listed under Legacy Property Names. It must not inspect
nested objects.

Migration decisions use key presence. If both an old and new name are
present, migration must fail even when either value is null, false, empty, or
equal to the other value.

`CodeMeta.from_legacy_jsonld()` applies context normalization and legacy
migration, validates the result as CodeMeta v3, and returns the open
`CodeMeta` representation. This path is intentionally lossy. Callers must use
`from_jsonld()` when they do not request those transforms.

## Serialization and Nulls

`to_jsonld()` is the canonical serialization method. It emits JSON-LD aliases
and JSON-compatible values.

Null handling is:

- a declared optional field whose value is `None` is omitted, whether it was
  absent or explicitly supplied as `None`;
- an unknown extra whose value is null remains present, at every nesting
  depth; and
- an explicitly supplied `@context: null` remains present.

`@context` is the only declared optional field for which explicit null
presence affects serialization. The implementation need not track input
presence for other declared optional fields.

Therefore this input:

```json
{
  "@context": null,
  "@type": "SoftwareSourceCode",
  "futureProperty": null
}
```

must serialize with both `@context` and `futureProperty` still present and
null.

The serializer must not apply Pydantic's `exclude_none=True` blindly because
that would discard null-valued extras.

The package does not add custom `.dict()`, `.json()`, or `.yaml()` methods.
Pydantic's contemporary `model_dump()` APIs remain available for callers who
need non-JSON-LD representations.

## Round-Trip Requirement

Ordinary parsing and serialization must satisfy model-equivalent round trips:

```python
parsed = Model.from_jsonld(original)
serialized = parsed.to_jsonld()
reparsed = Model.from_jsonld(serialized)

assert reparsed.model_dump(mode="python") == parsed.model_dump(mode="python")
```

This invariant applies to:

- known typed fields;
- unknown scalars, arrays, objects, and nulls;
- unknown values nested inside known models;
- context strings, objects, arrays, null entries, and explicit null context;
- `@type` and `@id`;
- unfamiliar `CreativeWork` subtype names;
- dates after documented conversion; and
- both scalar and repeated forms in the normative mapping table.

The invariant compares model meaning, not source text. Object key order,
whitespace, numeric spelling, and the lexical form of a parsed date need not
match the original JSON.

Explicit normalization and migration are outside this guarantee. Their
documented losses must remain isolated to the requested transform.

## Version Evolution

Future CodeMeta support should normally require only:

- adding or changing typed fields after updating this inventory;
- adding a version-specific binding when a context constraint is useful;
- adding tests; and
- adding migration code only for an authoritative, required migration.

Future support must not require a new parser, a closed extra-property policy,
or a replacement class hierarchy. A future context and future property must
already be preservable by the open `CodeMeta` model before the package adds
typed support for them.

## Required Tests

Tests must cover:

- Python-name and alias construction;
- presence-based alias collisions, including equal and null values;
- correct fixed `@type` values;
- `@id` preservation;
- context strings, objects, arrays, null entries, and explicit null;
- future context preservation by `CodeMeta`;
- v3 context enforcement by `CodeMetaV3`;
- unknown scalar, array, object, prefixed, keyword, nested, and null values;
- rejection of every non-JSON raw-value category listed in this document;
- canonical and legacy property coexistence during ordinary parsing;
- explicit legacy migration and collision rejection;
- intentionally lossy context normalization;
- the `CreativeWork` fallback and known-incompatible rejection;
- each scalar and repeated form in the normative mapping table;
- valid dates, malformed strings, datetime strings, and invalid date inputs;
- open-to-v3 and v3-to-open conversion; and
- the second-parse round-trip invariant.

## Acceptance Criteria

The model layer conforms to this specification when:

1. Every model and typed field in the required inventory exists.
1. Known fields use explicit types and JSON-LD aliases.
1. Unknown JSON-compatible values survive recursively without inference.
1. Non-JSON unknown values are rejected without coercion.
1. `from_jsonld()` performs validation without normalization or migration.
1. Explicit transforms have only their documented effects and losses.
1. Context, type, identifier, alias, date, null, fallback, and cardinality
   behavior match this document.
1. Parse, serialize, and reparse produce equivalent model state.
1. Automated tests enforce these requirements.
1. The open model can preserve future contexts and properties without
   knowing a future vocabulary.
