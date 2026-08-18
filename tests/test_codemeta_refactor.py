from __future__ import annotations

import pytest
from pydantic import ValidationError

from pydantic_codemeta import (
    CODEMETA_V3_CONTEXT,
    CodeMeta,
    CodeMetaV3,
    codemeta_to_codemeta_v3,
    codemeta_v3_to_codemeta,
    migrate_legacy_codemeta,
    normalize_jsonld_context,
)


def test_models_keep_boundaries_and_aliases() -> None:
    model = CodeMetaV3.model_validate(
        {"context": CODEMETA_V3_CONTEXT, "type": "SoftwareSourceCode", "name": "x"}
    )
    assert model.to_jsonld()["@context"] == CODEMETA_V3_CONTEXT
    assert CodeMeta(context="future", type="SoftwareSourceCode").context == "future"
    with pytest.raises(ValidationError):
        CodeMetaV3.model_validate({"@context": "future", "@type": "SoftwareSourceCode"})
    with pytest.raises(ValidationError):
        CodeMetaV3.model_validate({"@context": CODEMETA_V3_CONTEXT, "@type": "SoftwareApplication"})
    with pytest.raises(ValidationError):
        CodeMeta(type="SoftwareApplication")


def test_normalization_is_root_only_lossy_and_non_mutating() -> None:
    nested = {"schema:name": "nested"}
    data = {"@context": {"schema": "https://schema.org/", "ex": "urn:ex"},
            "schema:name": "x", "ex:version": 1, "unknown:value": 2, "nested": nested}
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


def test_migration_checks_presence_and_is_shallow() -> None:
    nested = {"creator": "keep"}
    data = {"embargoDate": "", "contIntegration": [], "creator": nested}
    result = migrate_legacy_codemeta(data)
    assert result == {"embargoEndDate": "", "continuousIntegration": [], "author": nested}
    assert data["creator"] is nested


@pytest.mark.parametrize(
    ("old", "new"),
    [("embargoDate", "embargoEndDate"),
     ("contIntegration", "continuousIntegration"),
     ("creator", "author")],
)
def test_migration_rejects_each_key_presence_collision(old: str, new: str) -> None:
    with pytest.raises(ValueError):
        migrate_legacy_codemeta({old: None, new: ""})


def test_compatibility_shim_and_adapters_preserve_extras() -> None:
    model = CodeMeta.from_jsonld({
        "@context": {"schema": "https://schema.org/"},
        "@type": "SoftwareSourceCode",
        "schema:name": "tool",
        "creator": "author",
        "futureField": {"raw": True},
    })
    assert model.name == "tool"
    assert model.author == "author"
    assert model.futureField == {"raw": True}
    v3 = codemeta_to_codemeta_v3(model)
    assert codemeta_v3_to_codemeta(v3).futureField == {"raw": True}
    assert CodeMeta().context == CODEMETA_V3_CONTEXT
    assert codemeta_to_codemeta_v3(CodeMeta(context=None)).context == CODEMETA_V3_CONTEXT
    with pytest.raises(ValueError):
        codemeta_to_codemeta_v3(CodeMeta(context="future"))
