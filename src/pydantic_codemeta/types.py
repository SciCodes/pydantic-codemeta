"""Typed schema.org and CodeMeta vocabulary terms used by the package."""

from __future__ import annotations

from datetime import date, datetime
from typing import Literal, TypeAlias

from pydantic import Field, StrictBool, StrictFloat, StrictInt, field_validator

from .base import JsonLdContext, PropertyValue, RawJsonObject, Thing


def _parse_iso_date(value: object) -> date | str | None:
    """Parse ISO dates while preserving other strings verbatim."""

    if value is None:
        return None
    if isinstance(value, datetime):
        raise ValueError("datetime values are not accepted for date fields")
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError("date fields accept only date objects or strings")
    try:
        return date.fromisoformat(value)
    except ValueError:
        return value


_NON_CREATIVE_WORK_TYPES = {
    "Thing",
    "Person",
    "Organization",
    "Role",
    "ContactPoint",
    "PostalAddress",
    "ComputerLanguage",
    "PropertyValue",
}


class ContactPoint(Thing):
    """A schema.org contact point."""

    type: Literal["ContactPoint"] = Field("ContactPoint", alias="@type")
    contact_type: str | None = Field(None, alias="contactType")
    email: str | None = None


class PostalAddress(Thing):
    """A schema.org postal address."""

    type: Literal["PostalAddress"] = Field("PostalAddress", alias="@type")
    street_address: str | None = Field(None, alias="streetAddress")
    address_locality: str | None = Field(None, alias="addressLocality")
    address_region: str | None = Field(None, alias="addressRegion")
    postal_code: str | None = Field(None, alias="postalCode")
    address_country: str | None = Field(None, alias="addressCountry")


class Organization(Thing):
    """A schema.org organization."""

    type: Literal["Organization"] = Field("Organization", alias="@type")
    email: str | None = None
    contact_point: ContactPoint | list[ContactPoint] | None = Field(
        None, alias="contactPoint"
    )
    address: PostalAddress | str | None = None


class Person(Thing):
    """A schema.org person."""

    type: Literal["Person"] = Field("Person", alias="@type")
    email: str | None = None
    given_name: str | None = Field(None, alias="givenName")
    family_name: str | None = Field(None, alias="familyName")
    affiliation: Organization | str | None = None
    contact_point: ContactPoint | list[ContactPoint] | None = Field(
        None, alias="contactPoint"
    )
    address: PostalAddress | str | None = None


class Role(Thing):
    """A schema.org role associating an agent with a contribution."""

    type: Literal["Role"] = Field("Role", alias="@type")
    role_name: str | None = Field(None, alias="roleName")
    start_date: date | str | None = Field(None, alias="startDate")
    end_date: date | str | None = Field(None, alias="endDate")
    author: Person | Organization | str | None = None

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def parse_role_dates(cls, value: object) -> date | str | None:
        return _parse_iso_date(value)


class ComputerLanguage(Thing):
    """A schema.org computer programming language."""

    type: Literal["ComputerLanguage"] = Field("ComputerLanguage", alias="@type")


Agent: TypeAlias = Person | Organization | Role | str
AgentField: TypeAlias = Agent | list[Agent]
Party: TypeAlias = Person | Organization | str
PartyField: TypeAlias = Party | list[Party]


class CreativeWork(Thing):
    """Open CreativeWork relation model and base for known concrete subtypes.

    The type remains open so an unfamiliar CreativeWork subtype can retain its
    declared ``@type`` when it appears in a typed relationship field.
    """

    type: str = Field("CreativeWork", alias="@type")
    author: AgentField | None = None
    contributor: AgentField | None = None
    editor: Person | list[Person] | None = None
    publisher: PartyField | None = None
    copyright_holder: PartyField | None = Field(None, alias="copyrightHolder")
    copyright_year: StrictInt | None = Field(None, alias="copyrightYear")
    funder: PartyField | None = None
    sponsor: PartyField | None = None
    provider: PartyField | None = None
    producer: PartyField | None = None
    license: CreativeWork | str | list[CreativeWork | str] | None = None
    citation: (
        ScholarlyArticle
        | CreativeWork
        | str
        | list[ScholarlyArticle | CreativeWork | str]
        | None
    ) = None
    review: Review | str | None = None
    is_part_of: CreativeWork | str | list[CreativeWork | str] | None = Field(
        None, alias="isPartOf"
    )
    has_part: CreativeWork | str | list[CreativeWork | str] | None = Field(
        None, alias="hasPart"
    )
    encoding: MediaObject | list[MediaObject] | None = None
    keywords: str | list[str] | None = None
    position: StrictInt | str | None = None
    date_created: date | str | None = Field(None, alias="dateCreated")
    date_modified: date | str | None = Field(None, alias="dateModified")
    date_published: date | str | None = Field(None, alias="datePublished")

    @field_validator("date_created", "date_modified", "date_published", mode="before")
    @classmethod
    def parse_dates(cls, value: object) -> date | str | None:
        return _parse_iso_date(value)

    @field_validator("type")
    @classmethod
    def reject_known_non_creative_work_type(cls, value: str) -> str:
        if value in _NON_CREATIVE_WORK_TYPES:
            raise ValueError(f"{value} is not a CreativeWork type")
        return value


class MediaObject(CreativeWork):
    """A schema.org media object used by ``encoding``."""

    type: Literal["MediaObject"] = Field("MediaObject", alias="@type")
    content_url: str | None = Field(None, alias="contentUrl")
    encoding_format: str | None = Field(None, alias="encodingFormat")
    content_size: str | None = Field(None, alias="contentSize")


class DataFeed(CreativeWork):
    """A schema.org data feed used by ``supportingData``."""

    type: Literal["DataFeed"] = Field("DataFeed", alias="@type")
    data_feed_element: (
        str | RawJsonObject | list[str | RawJsonObject] | None
    ) = Field(None, alias="dataFeedElement")


class Review(CreativeWork):
    """A schema.org review."""

    type: Literal["Review"] = Field("Review", alias="@type")
    review_body: str | None = Field(None, alias="reviewBody")
    review_aspect: str | None = Field(None, alias="reviewAspect")


class ScholarlyArticle(CreativeWork):
    """A schema.org scholarly article."""

    type: Literal["ScholarlyArticle"] = Field("ScholarlyArticle", alias="@type")


class SoftwareSourceCode(CreativeWork):
    """Stable, version-neutral SoftwareSourceCode information model."""

    context: JsonLdContext = Field(None, alias="@context")
    type: Literal["SoftwareSourceCode"] = Field(
        "SoftwareSourceCode", alias="@type"
    )
    code_repository: str | None = Field(None, alias="codeRepository")
    programming_language: (
        ComputerLanguage | str | list[ComputerLanguage | str] | None
    ) = Field(None, alias="programmingLanguage")
    runtime_platform: str | list[str] | None = Field(None, alias="runtimePlatform")
    target_product: (
        SoftwareApplication | str | list[SoftwareApplication | str] | None
    ) = Field(None, alias="targetProduct")
    application_category: str | list[str] | None = Field(
        None, alias="applicationCategory"
    )
    application_sub_category: str | list[str] | None = Field(
        None, alias="applicationSubCategory"
    )
    download_url: str | list[str] | None = Field(None, alias="downloadUrl")
    file_size: str | None = Field(None, alias="fileSize")
    install_url: str | list[str] | None = Field(None, alias="installUrl")
    memory_requirements: str | list[str] | None = Field(
        None, alias="memoryRequirements"
    )
    operating_system: str | list[str] | None = Field(None, alias="operatingSystem")
    permissions: str | list[str] | None = None
    processor_requirements: str | list[str] | None = Field(
        None, alias="processorRequirements"
    )
    release_notes: str | list[str] | None = Field(None, alias="releaseNotes")
    software_help: CreativeWork | str | list[CreativeWork | str] | None = Field(
        None, alias="softwareHelp"
    )
    software_requirements: (
        SoftwareSourceCode | str | list[SoftwareSourceCode | str] | None
    ) = Field(None, alias="softwareRequirements")
    software_version: str | None = Field(None, alias="softwareVersion")
    storage_requirements: str | list[str] | None = Field(
        None, alias="storageRequirements"
    )
    file_format: str | list[str] | None = Field(None, alias="fileFormat")
    is_accessible_for_free: StrictBool | None = Field(
        None, alias="isAccessibleForFree"
    )
    version: (
        StrictInt
        | StrictFloat
        | str
        | list[StrictInt | StrictFloat | str]
        | None
    ) = None
    supporting_data: DataFeed | list[DataFeed] | None = Field(
        None, alias="supportingData"
    )

    # CodeMeta-specific vocabulary terms.
    maintainer: AgentField | None = None
    build_instructions: str | list[str] | None = Field(
        None, alias="buildInstructions"
    )
    continuous_integration: str | list[str] | None = Field(
        None, alias="continuousIntegration"
    )
    development_status: str | None = Field(None, alias="developmentStatus")
    embargo_end_date: date | str | None = Field(None, alias="embargoEndDate")
    funding: str | list[str] | None = None
    has_source_code: (
        SoftwareSourceCode | str | list[SoftwareSourceCode | str] | None
    ) = Field(None, alias="hasSourceCode")
    is_source_code_of: (
        SoftwareApplication | str | list[SoftwareApplication | str] | None
    ) = Field(None, alias="isSourceCodeOf")
    issue_tracker: str | list[str] | None = Field(None, alias="issueTracker")
    readme: str | list[str] | None = None
    reference_publication: (
        ScholarlyArticle | str | list[ScholarlyArticle | str] | None
    ) = Field(None, alias="referencePublication")
    software_suggestions: (
        SoftwareSourceCode | str | list[SoftwareSourceCode | str] | None
    ) = Field(None, alias="softwareSuggestions")

    @field_validator("embargo_end_date", mode="before")
    @classmethod
    def parse_embargo_date(cls, value: object) -> date | str | None:
        return _parse_iso_date(value)


class SoftwareApplication(CreativeWork):
    """A schema.org SoftwareApplication model."""

    type: Literal["SoftwareApplication"] = Field(
        "SoftwareApplication", alias="@type"
    )
    application_category: str | list[str] | None = Field(
        None, alias="applicationCategory"
    )
    application_sub_category: str | list[str] | None = Field(
        None, alias="applicationSubCategory"
    )
    operating_system: str | list[str] | None = Field(None, alias="operatingSystem")
    software_version: str | None = Field(None, alias="softwareVersion")
    download_url: str | list[str] | None = Field(None, alias="downloadUrl")
    install_url: str | list[str] | None = Field(None, alias="installUrl")
    memory_requirements: str | list[str] | None = Field(
        None, alias="memoryRequirements"
    )
    processor_requirements: str | list[str] | None = Field(
        None, alias="processorRequirements"
    )
    storage_requirements: str | list[str] | None = Field(
        None, alias="storageRequirements"
    )
    permissions: str | list[str] | None = None
    supporting_data: DataFeed | list[DataFeed] | None = Field(
        None, alias="supportingData"
    )


CreativeWork.model_rebuild()
MediaObject.model_rebuild()
DataFeed.model_rebuild()
Review.model_rebuild()
ScholarlyArticle.model_rebuild()
SoftwareSourceCode.model_rebuild()
SoftwareApplication.model_rebuild()
Role.model_rebuild()
Person.model_rebuild()
Organization.model_rebuild()
