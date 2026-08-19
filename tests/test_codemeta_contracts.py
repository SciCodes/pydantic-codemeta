from __future__ import annotations

from datetime import date, datetime
from enum import IntEnum

import pytest
from pydantic import BaseModel, ValidationError

from pydantic_codemeta import (
    CODEMETA_V3_CONTEXT,
    CodeMeta,
    CodeMetaV3,
    ComputerLanguage,
    CreativeWork,
    Person,
    SchemaOrgBase,
    SoftwareSourceCode,
    codemeta_to_codemeta_v3,
    codemeta_v3_to_codemeta,
    migrate_legacy_codemeta,
    normalize_jsonld_context,
)


class _ArbitraryModel(BaseModel):
    value: int = 1


class _JsonLikeInt(IntEnum):
    VALUE = 1


def test_codemeta_accepts_python_names_for_jsonld_keywords() -> None:
    model = CodeMetaV3.model_validate(
        {"context": CODEMETA_V3_CONTEXT, "type": "SoftwareSourceCode", "name": "x"}
    )
    assert model.to_jsonld()["@context"] == CODEMETA_V3_CONTEXT


def test_codemeta_preserves_non_v3_string_context() -> None:
    assert CodeMeta(context="future", type="SoftwareSourceCode").context == "future"


def test_codemeta_v3_requires_v3_context() -> None:
    with pytest.raises(ValidationError):
        CodeMetaV3.model_validate({"@context": "future", "@type": "SoftwareSourceCode"})


def test_codemeta_models_require_software_source_code_type() -> None:
    with pytest.raises(ValidationError):
        CodeMetaV3.model_validate(
            {"@context": CODEMETA_V3_CONTEXT, "@type": "SoftwareApplication"}
        )
    with pytest.raises(ValidationError):
        CodeMeta(type="SoftwareApplication")


def test_version_binding_specializes_open_model() -> None:
    assert issubclass(CodeMetaV3, CodeMeta)
    assert issubclass(CodeMeta, SoftwareSourceCode)


def test_python_names_serialize_as_jsonld_aliases() -> None:
    model = CodeMeta(
        code_repository="https://example.org/repository",
        date_published=date(2024, 6, 1),
        continuous_integration="https://ci.example.org/build",
        author=Person(given_name="Ada", family_name="Lovelace"),
    )

    assert model.to_jsonld() == {
        "@type": "SoftwareSourceCode",
        "@context": CODEMETA_V3_CONTEXT,
        "author": {
            "@type": "Person",
            "givenName": "Ada",
            "familyName": "Lovelace",
        },
        "datePublished": "2024-06-01",
        "codeRepository": "https://example.org/repository",
        "continuousIntegration": "https://ci.example.org/build",
    }


@pytest.mark.parametrize(
    "payload",
    [
        {"@type": "SoftwareSourceCode", "type": "SoftwareSourceCode"},
        {"@type": "SoftwareSourceCode", "@context": "x", "context": "x"},
        {
            "@type": "SoftwareSourceCode",
            "codeRepository": "https://example.org/a",
            "code_repository": "https://example.org/b",
        },
        {
            "@type": "SoftwareSourceCode",
            "codeRepository": None,
            "code_repository": None,
        },
    ],
)
def test_alias_and_python_name_collisions_are_rejected(
    payload: dict[str, object],
) -> None:
    with pytest.raises(ValidationError, match="Conflicting field name"):
        CodeMeta.model_validate(payload)


def test_normalization_is_root_only_lossy_and_non_mutating() -> None:
    nested = {"schema:name": "nested"}
    data = {
        "@context": {"schema": "https://schema.org/", "ex": "urn:ex"},
        "schema:name": "x",
        "ex:version": 1,
        "unknown:value": 2,
        "nested": nested,
    }
    result = normalize_jsonld_context(data)
    assert result == {"name": "x", "version": 1, "unknown:value": 2, "nested": nested}
    assert data["@context"]
    assert result["nested"] is nested
    with pytest.raises(ValueError):
        normalize_jsonld_context({"@context": {"s": "urn:s"}, "s:name": 1, "name": 2})


@pytest.mark.parametrize("context", ["https://example.org/context", ["context"], 42])
def test_normalization_preserves_non_dict_context(context: object) -> None:
    data = {"@context": context, "name": "x"}
    result = normalize_jsonld_context(data)
    assert result == data


def test_normalization_preserves_unknown_prefix_keys() -> None:
    data = {"@context": {"schema": "https://schema.org/"}, "other:name": "x"}
    result = normalize_jsonld_context(data)
    assert result["other:name"] == "x"
    assert "@context" not in result


def test_normalization_does_not_treat_jsonld_keywords_as_prefixes() -> None:
    data = {
        "@context": {
            "@vocab": "https://schema.org/",
            "schema": "https://schema.org/",
        },
        "@vocab:name": "unchanged",
        "schema:name": "flattened",
    }

    assert normalize_jsonld_context(data) == {
        "@vocab:name": "unchanged",
        "name": "flattened",
    }


def test_legacy_migration_renames_root_keys_and_preserves_nested_values() -> None:
    nested = {"creator": "keep"}
    data = {"embargoDate": "", "contIntegration": [], "creator": nested}
    result = migrate_legacy_codemeta(data)
    assert result == {
        "embargoEndDate": "",
        "continuousIntegration": [],
        "author": nested,
    }
    assert data["creator"] is nested


@pytest.mark.parametrize(
    ("old", "new"),
    [
        ("embargoDate", "embargoEndDate"),
        ("contIntegration", "continuousIntegration"),
        ("creator", "author"),
    ],
)
def test_migration_rejects_each_key_presence_collision(old: str, new: str) -> None:
    with pytest.raises(ValueError):
        migrate_legacy_codemeta({old: None, new: ""})


def test_from_jsonld_is_pure_parse_preserves_dict_context() -> None:
    """from_jsonld must not normalize or migrate — it preserves input verbatim."""

    data = {
        "@context": {"schema": "https://schema.org/"},
        "@type": "SoftwareSourceCode",
        "schema:name": "tool",
        "creator": "author",
        "futureField": {"raw": True},
    }
    model = CodeMeta.from_jsonld(data)
    # Dict context preserved as-is (no normalization, no v3 backfill)
    assert model.context == {"schema": "https://schema.org/"}
    # No migration: creator stays as an extra, author stays None
    assert model.model_extra["creator"] == "author"
    assert model.author is None
    # Prefixed key preserved as extra (not flattened)
    assert model.model_extra["schema:name"] == "tool"
    assert model.futureField == {"raw": True}


def test_from_jsonld_preserves_non_v3_string_context() -> None:
    """from_jsonld must accept any string context, not just v3."""

    model = CodeMeta.from_jsonld(
        {
            "@context": "https://w3id.org/codemeta/4.0",
            "@type": "SoftwareSourceCode",
            "name": "Tool",
        }
    )
    assert model.context == "https://w3id.org/codemeta/4.0"
    assert model.to_jsonld()["@context"] == "https://w3id.org/codemeta/4.0"


@pytest.mark.parametrize(
    "context",
    [
        {"schema": "https://schema.org/", "@vocab": "https://schema.org/"},
        [
            "https://w3id.org/codemeta/3.0",
            {"ex": "https://example.org/"},
            None,
        ],
    ],
)
def test_open_model_preserves_supported_context_shapes(context: object) -> None:
    model = CodeMeta.from_jsonld(
        {"@context": context, "@type": "SoftwareSourceCode", "name": "Tool"}
    )

    assert model.context == context
    assert model.to_jsonld()["@context"] == context


@pytest.mark.parametrize("context", [42, True, {"term": object()}])
def test_open_model_rejects_non_jsonld_context_shapes(context: object) -> None:
    with pytest.raises(ValidationError):
        CodeMeta(context=context)


def test_explicit_null_context_is_preserved() -> None:
    model = CodeMeta.from_jsonld(
        {"@context": None, "@type": "SoftwareSourceCode", "name": "Tool"}
    )

    assert model.context is None
    assert model.to_jsonld()["@context"] is None


def test_unknown_json_values_and_keywords_round_trip_without_inference() -> None:
    unknown = {
        "futureScalar": 3.5,
        "futureNull": None,
        "futureList": [1, "two", False, None],
        "futureNode": {
            "@type": "FutureType",
            "nestedTerm": {"raw": True, "futureNull": None},
        },
        "@graph": [{"@id": "urn:example:item", "future": "value"}],
        "ex:future": {"values": [1, 2, 3]},
        "model_dump": "collides with a Python method name",
    }
    model = CodeMeta.from_jsonld(
        {"@type": "SoftwareSourceCode", "name": "Tool", **unknown}
    )

    assert model.model_extra == unknown
    serialized = model.to_jsonld()
    for key, value in unknown.items():
        assert serialized[key] == value
    assert model.model_extra["model_dump"] == unknown["model_dump"]


def test_unknown_properties_inside_known_nodes_remain_raw() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@type": "SoftwareSourceCode",
            "author": {
                "@type": "Person",
                "name": "Ada",
                "futureAgentTerm": {"@type": "FutureNode", "raw": [1, 2]},
                "futureAgentNull": None,
            },
        }
    )

    assert isinstance(model.author, Person)
    assert model.author.model_extra == {
        "futureAgentTerm": {"@type": "FutureNode", "raw": [1, 2]},
        "futureAgentNull": None,
    }
    assert model.to_jsonld()["author"]["futureAgentTerm"] == {
        "@type": "FutureNode",
        "raw": [1, 2],
    }
    assert model.to_jsonld()["author"]["futureAgentNull"] is None


@pytest.mark.parametrize(
    "value",
    [
        (1, 2),
        {1, 2},
        date(2024, 1, 2),
        datetime(2024, 1, 2, 3, 4),
        object(),
        _ArbitraryModel(),
        {1: "non-string key"},
        {"nested": (1, 2)},
        _JsonLikeInt.VALUE,
    ],
)
def test_unknown_non_json_value_is_rejected(value: object) -> None:
    with pytest.raises(ValidationError):
        CodeMeta.model_validate({"@type": "SoftwareSourceCode", "futureObject": value})


@pytest.mark.parametrize(
    "value",
    [
        float("nan"),
        float("inf"),
        float("-inf"),
        {"nested": [float("nan")]},
    ],
)
def test_unknown_non_finite_json_numbers_are_rejected(value: object) -> None:
    with pytest.raises(ValidationError):
        CodeMeta.model_validate({"@type": "SoftwareSourceCode", "futureNumber": value})


def test_context_object_rejects_nested_non_finite_json_numbers() -> None:
    with pytest.raises(ValidationError):
        CodeMeta(context={"term": {"weight": float("inf")}})


def test_computer_language_preserves_future_properties_as_extras() -> None:
    language = ComputerLanguage.from_jsonld(
        {"@type": "ComputerLanguage", "name": "Python", "version": "3.13"}
    )

    assert language.model_extra == {"version": "3.13"}
    assert language.to_jsonld()["version"] == "3.13"


def test_pure_parse_preserves_canonical_and_legacy_names_together() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@type": "SoftwareSourceCode",
            "author": "canonical",
            "creator": "legacy",
            "continuousIntegration": "canonical-ci",
            "contIntegration": "legacy-ci",
        }
    )

    assert model.author == "canonical"
    assert model.continuous_integration == "canonical-ci"
    assert model.model_extra == {
        "creator": "legacy",
        "contIntegration": "legacy-ci",
    }
    assert model.to_jsonld()["creator"] == "legacy"


def test_from_legacy_jsonld_normalizes_and_migrates() -> None:
    """from_legacy_jsonld flattens dict context, migrates legacy keys, backfills v3."""

    model = CodeMeta.from_legacy_jsonld(
        {
            "@context": {"schema": "https://schema.org/"},
            "@type": "SoftwareSourceCode",
            "schema:name": "tool",
            "creator": "author",
            "futureField": {"raw": True},
        }
    )
    assert model.name == "tool"
    assert model.author == "author"
    assert "creator" not in (model.model_extra or {})
    assert model.context == CODEMETA_V3_CONTEXT
    assert model.futureField == {"raw": True}

    v3 = CodeMetaV3.from_legacy_jsonld(
        {
            "@context": {"schema": "https://schema.org/"},
            "@type": "SoftwareSourceCode",
            "schema:name": "tool",
            "creator": "author",
        }
    )
    assert type(v3) is CodeMetaV3
    assert v3.context == CODEMETA_V3_CONTEXT


def test_from_legacy_jsonld_rejects_non_v3_context() -> None:
    """from_legacy_jsonld routes through CodeMetaV3, which rejects non-v3 contexts."""

    with pytest.raises(ValidationError):
        CodeMeta.from_legacy_jsonld(
            {
                "@context": "https://w3id.org/codemeta/4.0",
                "@type": "SoftwareSourceCode",
                "name": "Tool",
            }
        )


def test_v3_adapters_preserve_unknown_properties() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@context": CODEMETA_V3_CONTEXT,
            "@type": "SoftwareSourceCode",
            "name": "tool",
            "futureField": {"raw": True},
        }
    )
    v3 = codemeta_to_codemeta_v3(model)
    assert codemeta_v3_to_codemeta(v3).futureField == {"raw": True}


def test_v3_adapter_backfills_missing_or_null_context() -> None:
    assert CodeMeta().context == CODEMETA_V3_CONTEXT
    assert (
        codemeta_to_codemeta_v3(CodeMeta(context=None)).context == CODEMETA_V3_CONTEXT
    )


def test_v3_adapter_rejects_non_v3_string_context() -> None:
    with pytest.raises(ValueError):
        codemeta_to_codemeta_v3(CodeMeta(context="future"))


@pytest.mark.parametrize(
    "context",
    [
        {"schema": "https://schema.org/"},
        [CODEMETA_V3_CONTEXT, {"ex": "https://example.org/"}],
    ],
)
def test_v3_adapter_rejects_structured_contexts(context: object) -> None:
    with pytest.raises(ValueError):
        codemeta_to_codemeta_v3(CodeMeta(context=context))


def test_dates_parse_iso_dates_and_preserve_native_dates_and_other_strings() -> None:
    native = date(2024, 1, 2)
    model = CodeMeta(
        date_created=native,
        date_modified="2024-03-04",
        date_published="2024-03-04T05:06:07Z",
        embargo_end_date="not-a-date",
    )

    assert model.date_created is native
    assert model.date_modified == date(2024, 3, 4)
    assert model.date_published == "2024-03-04T05:06:07Z"
    assert model.embargo_end_date == "not-a-date"
    assert model.to_jsonld()["dateModified"] == "2024-03-04"


@pytest.mark.parametrize("value", [123, 1.5, datetime(2024, 1, 2, 3, 4)])
def test_date_fields_reject_numbers_and_datetimes(value: object) -> None:
    with pytest.raises(ValidationError):
        CodeMeta(date_created=value)


@pytest.mark.parametrize(
    ("model_type", "field", "value"),
    [
        (CreativeWork, "copyright_year", True),
        (CreativeWork, "position", True),
        (CodeMeta, "version", True),
        (CodeMeta, "is_accessible_for_free", 1),
    ],
)
def test_known_numeric_and_boolean_fields_do_not_coerce_other_json_types(
    model_type: type[SchemaOrgBase], field: str, value: object
) -> None:
    with pytest.raises(ValidationError):
        model_type(**{field: value})


@pytest.mark.parametrize(
    ("alias", "python_name", "scalar", "repeated"),
    [
        (
            "programmingLanguage",
            "programming_language",
            {"@type": "ComputerLanguage", "name": "Python"},
            [{"@type": "ComputerLanguage", "name": "Python"}, "R"],
        ),
        (
            "license",
            "license",
            {"@type": "Dataset", "name": "License terms"},
            [{"@type": "Dataset", "name": "License terms"}, "MIT"],
        ),
        (
            "identifier",
            "identifier",
            {"@type": "PropertyValue", "value": "10.1234/example"},
            [
                {"@type": "PropertyValue", "value": "10.1234/example"},
                "urn:example:tool",
            ],
        ),
        (
            "citation",
            "citation",
            {"@type": "ScholarlyArticle", "name": "A paper"},
            [
                {"@type": "ScholarlyArticle", "name": "A paper"},
                "https://example.org/paper",
            ],
        ),
        (
            "author",
            "author",
            {"@type": "Person", "name": "Ada"},
            [{"@type": "Person", "name": "Ada"}, "Research group"],
        ),
        (
            "contributor",
            "contributor",
            {"@type": "Organization", "name": "Example Lab"},
            [
                {"@type": "Organization", "name": "Example Lab"},
                "Community",
            ],
        ),
        (
            "maintainer",
            "maintainer",
            {"@type": "Role", "roleName": "Maintenance"},
            [
                {"@type": "Role", "roleName": "Maintenance"},
                "maintainers@example.org",
            ],
        ),
    ],
)
def test_normative_relationships_preserve_scalar_and_repeated_forms(
    alias: str, python_name: str, scalar: object, repeated: list[object]
) -> None:
    scalar_model = CodeMeta.model_validate({alias: scalar})
    repeated_model = CodeMeta.model_validate({alias: repeated})

    assert not isinstance(getattr(scalar_model, python_name), list)
    assert isinstance(getattr(repeated_model, python_name), list)
    assert CodeMeta.from_jsonld(repeated_model.to_jsonld()).model_dump(
        mode="python"
    ) == repeated_model.model_dump(mode="python")


@pytest.mark.parametrize(
    "field",
    [
        "programmingLanguage",
        "license",
        "identifier",
        "citation",
        "author",
        "contributor",
        "maintainer",
    ],
)
def test_normative_relationships_reject_nested_lists(field: str) -> None:
    with pytest.raises(ValidationError):
        CodeMeta.model_validate({field: [["https://example.org/reference"]]})


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("copyright_year", [2024]),
        ("position", [1, 2]),
    ],
)
def test_singular_vocabulary_fields_reject_lists(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        CreativeWork(**{field: value})


def test_concrete_model_rejects_replacement_type() -> None:
    with pytest.raises(ValidationError):
        Person(type="Organization")


def test_codemeta_rejects_multivalued_type() -> None:
    with pytest.raises(ValidationError):
        CodeMeta.from_jsonld({"@type": ["SoftwareSourceCode", "FutureSoftwareType"]})


def test_model_round_trip_equivalence_includes_context_id_and_unknowns() -> None:
    original = {
        "@context": [CODEMETA_V3_CONTEXT, {"ex": "https://example.org/"}],
        "@type": "SoftwareSourceCode",
        "@id": "urn:example:tool",
        "datePublished": "2024-06-01",
        "author": {"@type": "Person", "givenName": "Ada"},
        "ex:future": {"nested": [1, True, None]},
    }

    parsed = CodeMeta.from_jsonld(original)
    reparsed = CodeMeta.from_jsonld(parsed.to_jsonld())

    assert reparsed.model_dump(mode="python") == parsed.model_dump(mode="python")
    assert reparsed.id == "urn:example:tool"
    assert reparsed.context == original["@context"]


def test_base_does_not_add_legacy_serialization_helpers() -> None:
    assert "dict" not in SchemaOrgBase.__dict__
    assert "json" not in SchemaOrgBase.__dict__
    assert "yaml" not in SchemaOrgBase.__dict__
