from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from codemeta_datamodel import CodeMeta, Organization, Person, PropertyValue


FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text())


def test_parse_minimal_fixture() -> None:
    model = CodeMeta.from_jsonld(load_fixture("minimal_codemeta.json"))

    assert model.context == "https://w3id.org/codemeta/3.0"
    assert model.type == "SoftwareSourceCode"
    assert model.name == "My Tool"
    assert isinstance(model.author, Person)
    assert model.author.email == "jane@example.com"


def test_parse_full_fixture_with_multiple_authors() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    assert isinstance(model.author, list)
    assert len(model.author) == 2
    assert isinstance(model.author[0], Person)
    assert isinstance(model.author[1], Organization)


def test_property_value_identifier_is_supported() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    assert isinstance(model.identifier, PropertyValue)
    assert model.identifier.propertyID == "doi"


def test_unknown_fields_survive_round_trip() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    payload = model.to_jsonld()

    assert payload["softwareRequirements"] == "Python >= 3.10"
    assert payload["@context"] == "https://w3id.org/codemeta/3.0"
    assert payload["@type"] == "SoftwareSourceCode"


def test_iso_dates_are_accepted() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    assert isinstance(model.dateCreated, date)
    assert isinstance(model.dateModified, date)
    assert isinstance(model.datePublished, date)
    assert model.to_jsonld()["datePublished"] == "2024-06-01"
