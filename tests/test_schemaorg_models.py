from __future__ import annotations

import pytest
from pydantic import ValidationError

from codemeta_datamodel import (
    CodeMeta,
    ContactPoint,
    Organization,
    Person,
    PropertyValue,
)


def test_alias_handling_uses_jsonld_names_on_dump() -> None:
    model = CodeMeta(
        context="https://w3id.org/codemeta/3.0",
        name="My Tool",
        author=Person(name="Jane Smith", email="jane@example.com"),
    )

    payload = model.to_jsonld()

    assert payload["@context"] == "https://w3id.org/codemeta/3.0"
    assert payload["@type"] == "SoftwareSourceCode"
    assert payload["author"]["@type"] == "Person"


def test_nested_models_parse_from_jsonld() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@context": "https://w3id.org/codemeta/3.0",
            "@type": "SoftwareSourceCode",
            "name": "Toolkit",
            "author": {
                "@type": "Person",
                "name": "Jane Smith",
                "affiliation": {
                    "@type": "Organization",
                    "name": "Example Lab",
                },
                "contactPoint": {
                    "@type": "ContactPoint",
                    "contactType": "support",
                    "email": "jane@example.com",
                },
            },
        }
    )

    assert isinstance(model.author, Person)
    assert isinstance(model.author.affiliation, Organization)
    assert isinstance(model.author.contactPoint, ContactPoint)


def test_jsonld_round_trip_preserves_unknown_fields() -> None:
    model = CodeMeta(
        name="Round Trip Tool",
        softwareRequirements="Python >= 3.10",
    )

    round_tripped = CodeMeta.from_jsonld(model.to_jsonld()).to_jsonld()

    assert round_tripped["softwareRequirements"] == "Python >= 3.10"


def test_property_value_includes_type_alias() -> None:
    identifier = PropertyValue(name="DOI", propertyID="doi", value="10.1234/example")

    assert identifier.to_jsonld()["@type"] == "PropertyValue"


def test_invalid_nested_type_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        CodeMeta(
            author={
                "@type": "ContactPoint",
                "contactType": "support",
            }
        )


def test_invalid_property_value_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        PropertyValue(value={"unexpected": "object"})
