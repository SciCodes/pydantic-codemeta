from __future__ import annotations

import pytest
from pydantic import ValidationError

from pydantic_codemeta import (
    CodeMeta,
    CodeMetaV3,
    ComputerLanguage,
    ContactPoint,
    CreativeWork,
    Organization,
    Person,
    PostalAddress,
    PropertyValue,
    Review,
    Role,
    ScholarlyArticle,
    SoftwareApplication,
    SoftwareSourceCode,
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
    assert isinstance(model.author.contact_point, ContactPoint)


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


# ---------------------------------------------------------------------------
# New type tests
# ---------------------------------------------------------------------------


def test_role_parses_and_round_trips() -> None:
    role = Role(
        roleName="maintainer",
        author=Person(name="Alex Doe"),
        startDate="2023-01-01",
        endDate="2024-06-01",
    )

    payload = role.to_jsonld()

    assert payload["@type"] == "Role"
    assert payload["roleName"] == "maintainer"
    assert payload["author"]["@type"] == "Person"
    assert payload["startDate"] == "2023-01-01"


def test_role_in_author_field() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@context": "https://w3id.org/codemeta/3.0",
            "@type": "SoftwareSourceCode",
            "name": "Tool with Role author",
            "author": {
                "@type": "Role",
                "roleName": "maintainer",
                "author": {
                    "@type": "Person",
                    "name": "Alex Doe",
                },
                "startDate": "2023-01-01",
            },
        }
    )

    assert isinstance(model.author, Role)
    assert model.author.role_name == "maintainer"
    assert isinstance(model.author.author, Person)
    assert model.author.author.name == "Alex Doe"


def test_creative_work_base_type() -> None:
    work = CreativeWork(name="A Paper")

    payload = work.to_jsonld()

    assert payload["@type"] == "CreativeWork"
    assert payload["name"] == "A Paper"


def test_scholarly_article_type() -> None:
    article = ScholarlyArticle(
        name="Smith et al. 2024. Research Toolkit.",
        url="https://doi.org/10.1000/example-paper",
    )

    payload = article.to_jsonld()

    assert payload["@type"] == "ScholarlyArticle"
    assert payload["url"] == "https://doi.org/10.1000/example-paper"


def test_unknown_creative_work_subtype_round_trips_as_generic_work() -> None:
    work = CreativeWork.model_validate(
        {"@type": "WebApplication", "name": "Example application"}
    )

    assert type(work) is CreativeWork
    assert work.to_jsonld()["@type"] == "WebApplication"


def test_scholarly_article_remains_known_citation_subtype() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@context": "https://w3id.org/codemeta/3.0",
            "@type": "SoftwareSourceCode",
            "citation": {
                "@type": "ScholarlyArticle",
                "name": "A paper",
            },
        }
    )

    assert isinstance(model.citation, ScholarlyArticle)


def test_scholarly_article_remains_known_subtype_in_repeated_citation() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@type": "SoftwareSourceCode",
            "citation": [
                {"@type": "ScholarlyArticle", "name": "A paper"},
                {"@type": "Dataset", "name": "Supporting data"},
            ],
        }
    )

    assert isinstance(model.citation, list)
    assert isinstance(model.citation[0], ScholarlyArticle)
    assert type(model.citation[1]) is CreativeWork


@pytest.mark.parametrize("field", ["citation", "license"])
@pytest.mark.parametrize("type_key", ["@type", "type"])
@pytest.mark.parametrize("type_name", ["Thing", "Person"])
def test_known_non_creative_work_relationship_is_rejected(
    field: str, type_key: str, type_name: str
) -> None:
    with pytest.raises(ValidationError):
        SoftwareSourceCode(**{field: {type_key: type_name, "name": "Invalid"}})


@pytest.mark.parametrize("field", ["citation", "license"])
def test_known_non_creative_work_in_list_is_rejected(field: str) -> None:
    with pytest.raises(ValidationError):
        SoftwareSourceCode(**{field: [{"@type": "Thing", "name": "Invalid"}]})


def test_unknown_creative_work_subtype_remains_generic_in_citation() -> None:
    model = SoftwareSourceCode(
        citation={"@type": "WebApplication", "name": "Web app"}
    )

    assert type(model.citation) is CreativeWork
    assert model.to_jsonld()["citation"]["@type"] == "WebApplication"


def test_software_application_is_valid_creative_work_citation() -> None:
    model = SoftwareSourceCode(
        citation={"@type": "SoftwareApplication", "name": "Desktop app"}
    )

    assert type(model.citation) is CreativeWork
    assert model.to_jsonld()["citation"]["@type"] == "SoftwareApplication"


def test_software_relations_accept_structured_and_string_references() -> None:
    model = SoftwareSourceCode(
        softwareRequirements=[
            {"@type": "SoftwareSourceCode", "name": "Desktop app"},
            "https://example.org/runtime",
        ],
        softwareSuggestions={"@type": "SoftwareSourceCode", "name": "Suggested app"},
        hasSourceCode=[
            {"@type": "SoftwareSourceCode", "name": "Source tree"},
            "https://example.org/source",
        ],
        isSourceCodeOf=[
            {"@type": "SoftwareApplication", "name": "Application"},
            "https://example.org/project",
        ],
    )

    assert isinstance(model.software_requirements[0], SoftwareSourceCode)
    assert model.software_requirements[1] == "https://example.org/runtime"
    assert isinstance(model.software_suggestions, SoftwareSourceCode)
    assert isinstance(model.has_source_code[0], SoftwareSourceCode)
    assert model.has_source_code[1] == "https://example.org/source"
    assert isinstance(model.is_source_code_of[0], SoftwareApplication)
    assert model.is_source_code_of[1] == "https://example.org/project"

    payload = model.to_jsonld()
    assert payload["softwareRequirements"][0]["@type"] == "SoftwareSourceCode"
    assert payload["softwareSuggestions"]["@type"] == "SoftwareSourceCode"
    assert payload["hasSourceCode"][0]["@type"] == "SoftwareSourceCode"
    assert payload["isSourceCodeOf"][0]["@type"] == "SoftwareApplication"


def test_software_relation_strings_remain_supported() -> None:
    model = SoftwareSourceCode(
        softwareRequirements="Python",
        softwareSuggestions=["R"],
        hasSourceCode="https://example.org/source",
        isSourceCodeOf=["https://example.org/project"],
    )

    assert model.software_requirements == "Python"
    assert model.software_suggestions == ["R"]
    assert model.has_source_code == "https://example.org/source"
    assert model.is_source_code_of == ["https://example.org/project"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("softwareRequirements", {"@type": "SoftwareApplication"}),
        ("softwareSuggestions", {"@type": "SoftwareApplication"}),
        ("hasSourceCode", {"@type": "CreativeWork"}),
        ("isSourceCodeOf", {"@type": "SoftwareSourceCode"}),
        ("isSourceCodeOf", {"@type": "CreativeWork"}),
    ],
)
def test_software_relations_reject_out_of_range_structured_values(
    field: str, value: dict[str, str]
) -> None:
    with pytest.raises(ValidationError):
        SoftwareSourceCode(**{field: value})


def test_raw_union_citation_classification() -> None:
    generic = SoftwareSourceCode(
        citation={"@type": "WebApplication", "name": "Web app"}
    )
    scholarly = SoftwareSourceCode(
        citation={"@type": "ScholarlyArticle", "name": "Paper"}
    )

    assert type(generic.citation) is CreativeWork
    assert isinstance(scholarly.citation, ScholarlyArticle)
    assert generic.to_jsonld()["citation"]["@type"] == "WebApplication"
    assert scholarly.to_jsonld()["citation"]["@type"] == "ScholarlyArticle"


def test_review_type() -> None:
    review = Review(
        reviewBody="Well-documented and reproducible.",
        reviewAspect="Documentation",
    )

    payload = review.to_jsonld()

    assert payload["@type"] == "Review"
    assert payload["reviewBody"] == "Well-documented and reproducible."
    assert payload["reviewAspect"] == "Documentation"


def test_postal_address_type() -> None:
    address = PostalAddress(
        streetAddress="123 Main St",
        addressLocality="Anytown",
        addressRegion="CA",
        postalCode="90210",
        addressCountry="US",
    )

    payload = address.to_jsonld()

    assert payload["@type"] == "PostalAddress"
    assert payload["streetAddress"] == "123 Main St"
    assert payload["addressCountry"] == "US"


def test_computer_language_type() -> None:
    lang = ComputerLanguage(name="Python")

    payload = lang.to_jsonld()

    assert payload["@type"] == "ComputerLanguage"
    assert payload["name"] == "Python"


def test_software_application_does_not_inherit_software_source_code_fields() -> None:
    app = SoftwareApplication(name="My App")

    payload = app.to_jsonld()

    assert payload["@type"] == "SoftwareApplication"
    # codeRepository is a SoftwareSourceCode field, not SoftwareApplication
    assert "codeRepository" not in payload
    assert "programmingLanguage" not in payload


def test_software_source_code_supports_computer_language_in_programming_language() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@context": "https://w3id.org/codemeta/3.0",
            "@type": "SoftwareSourceCode",
            "name": "Tool",
            "programmingLanguage": [
                {"@type": "ComputerLanguage", "name": "Python"},
                "R",
            ],
        }
    )

    assert isinstance(model.programming_language, list)
    assert isinstance(model.programming_language[0], ComputerLanguage)
    assert model.programming_language[0].name == "Python"
    assert model.programming_language[1] == "R"


def test_software_source_code_supports_creative_work_in_license() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@context": "https://w3id.org/codemeta/3.0",
            "@type": "SoftwareSourceCode",
            "name": "Tool",
            "license": {
                "@type": "CreativeWork",
                "name": "MIT License",
                "url": "https://spdx.org/licenses/MIT.html",
            },
        }
    )

    assert isinstance(model.license, CreativeWork)
    assert model.license.name == "MIT License"


def test_software_source_code_supports_creative_work_in_citation() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@context": "https://w3id.org/codemeta/3.0",
            "@type": "SoftwareSourceCode",
            "name": "Tool",
            "citation": {
                "@type": "ScholarlyArticle",
                "name": "Smith et al. 2024",
                "url": "https://doi.org/10.1000/example",
            },
        }
    )

    assert isinstance(model.citation, ScholarlyArticle)
    assert model.citation.url == "https://doi.org/10.1000/example"


def test_software_source_code_supports_review() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@context": "https://w3id.org/codemeta/3.0",
            "@type": "SoftwareSourceCode",
            "name": "Tool",
            "review": {
                "@type": "Review",
                "reviewBody": "Great software.",
                "reviewAspect": "Quality",
            },
        }
    )

    assert isinstance(model.review, Review)
    assert model.review.review_body == "Great software."


def test_same_as_field_preserved() -> None:
    model = CodeMeta.from_jsonld(
        {
            "@context": "https://w3id.org/codemeta/3.0",
            "@type": "SoftwareSourceCode",
            "name": "Tool",
            "sameAs": "https://example.org/mirror",
        }
    )

    assert model.same_as == "https://example.org/mirror"
    assert model.to_jsonld()["sameAs"] == "https://example.org/mirror"


def test_codemeta_rejects_non_3_0_context() -> None:
    with pytest.raises(ValidationError):
        CodeMetaV3.from_jsonld(
            {
                "@context": "https://w3id.org/codemeta/4.0",
                "@type": "SoftwareSourceCode",
                "name": "Tool",
            }
        )


def test_software_source_code_accepts_v4_context() -> None:
    """SoftwareSourceCode is not version-locked and should preserve any context."""

    model = SoftwareSourceCode.from_jsonld(
        {
            "@context": "https://w3id.org/codemeta/4.0",
            "@type": "SoftwareSourceCode",
            "name": "Tool",
        }
    )

    assert model.context == "https://w3id.org/codemeta/4.0"
    assert model.to_jsonld()["@context"] == "https://w3id.org/codemeta/4.0"
