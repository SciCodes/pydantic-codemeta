from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from pydantic_codemeta import (
    CodeMeta,
    ComputerLanguage,
    Organization,
    Person,
    PropertyValue,
    Review,
    Role,
    ScholarlyArticle,
)


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
    assert len(model.author) == 3
    assert isinstance(model.author[0], Person)
    assert isinstance(model.author[1], Organization)
    assert isinstance(model.author[2], Role)
    assert model.author[2].role_name == "maintainer"
    assert isinstance(model.author[2].author, Person)
    assert model.author[2].author.name == "Alex Doe"


def test_property_value_identifier_is_supported() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    assert isinstance(model.identifier, PropertyValue)
    assert model.identifier.property_id == "doi"


def test_unknown_fields_survive_round_trip() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    payload = model.to_jsonld()

    assert payload["softwareRequirements"] == "Python >= 3.10"
    assert payload["@context"] == "https://w3id.org/codemeta/3.0"
    assert payload["@type"] == "SoftwareSourceCode"


def test_iso_dates_parse_and_serialize() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    assert isinstance(model.date_created, date)
    assert isinstance(model.date_modified, date)
    assert isinstance(model.date_published, date)
    assert model.to_jsonld()["datePublished"] == "2024-06-01"


def test_role_dates_are_parsed() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    role = model.author[2]
    assert isinstance(role, Role)
    assert isinstance(role.start_date, date)
    assert isinstance(role.end_date, date)
    assert role.start_date == date(2023, 1, 1)
    assert role.end_date == date(2024, 6, 1)


def test_programming_language_supports_computer_language_objects() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    assert isinstance(model.programming_language, list)
    assert isinstance(model.programming_language[0], ComputerLanguage)
    assert model.programming_language[0].name == "Python"
    assert model.programming_language[1] == "R"


def test_citation_supports_scholarly_article() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    assert isinstance(model.citation, ScholarlyArticle)
    assert model.citation.url == "https://doi.org/10.1000/example-paper"


def test_reference_publication_supports_scholarly_article() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    assert isinstance(model.reference_publication, ScholarlyArticle)
    assert model.reference_publication.url == "https://doi.org/10.1000/example-paper"


def test_review_field_parses() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    assert isinstance(model.review, Review)
    assert model.review.review_body == "Well-documented and reproducible."
    assert model.review.review_aspect == "Documentation"


def test_codemeta_specific_fields_parse_from_fixture() -> None:
    model = CodeMeta.from_jsonld(load_fixture("full_codemeta.json"))

    assert model.issue_tracker == "https://github.com/example/research-toolkit/issues"
    assert model.readme == "https://github.com/example/research-toolkit/blob/main/README.md"
    assert model.build_instructions == "https://github.com/example/research-toolkit#building"
    assert model.development_status == "active"


def test_full_fixture_round_trips_semantically() -> None:
    """Round-trip serialization should preserve all known and unknown fields."""

    original = load_fixture("full_codemeta.json")
    model = CodeMeta.from_jsonld(original)
    round_tripped = model.to_jsonld()
    reparsed = CodeMeta.from_jsonld(round_tripped)

    assert reparsed.model_dump(mode="python") == model.model_dump(mode="python")

    # Core fields preserved
    assert round_tripped["@context"] == original["@context"]
    assert round_tripped["@type"] == original["@type"]
    assert round_tripped["name"] == original["name"]
    assert round_tripped["version"] == original["version"]

    # Nested author types preserved
    assert isinstance(round_tripped["author"], list)
    assert round_tripped["author"][0]["@type"] == "Person"
    assert round_tripped["author"][1]["@type"] == "Organization"
    assert round_tripped["author"][2]["@type"] == "Role"
    assert round_tripped["author"][2]["author"]["@type"] == "Person"

    # Dates preserved
    assert round_tripped["datePublished"] == original["datePublished"]

    # Programming language with mixed ComputerLanguage and str
    assert round_tripped["programmingLanguage"][0]["@type"] == "ComputerLanguage"
    assert round_tripped["programmingLanguage"][1] == "R"

    # Citation and referencePublication as ScholarlyArticle
    assert round_tripped["citation"]["@type"] == "ScholarlyArticle"
    assert round_tripped["referencePublication"]["@type"] == "ScholarlyArticle"

    # Review preserved
    assert round_tripped["review"]["@type"] == "Review"
    assert round_tripped["review"]["reviewBody"] == original["review"]["reviewBody"]

    # CodeMeta-specific fields preserved
    assert round_tripped["issueTracker"] == original["issueTracker"]
    assert round_tripped["developmentStatus"] == original["developmentStatus"]
