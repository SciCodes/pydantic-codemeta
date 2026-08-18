"""Concrete schema.org types used by CodeMeta."""

from __future__ import annotations

from datetime import date
from typing import Literal, TypeAlias

from pydantic import Field, field_validator

from .base import PropertyValue, Thing


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_iso_date(value: date | str | None) -> date | str | None:
    """Convert valid ISO date strings to ``date`` objects, preserving others."""

    if not isinstance(value, str):
        return value
    try:
        return date.fromisoformat(value)
    except ValueError:
        return value


_NON_CREATIVE_WORK_TYPES = {
    "Person",
    "Organization",
    "Role",
    "ContactPoint",
    "PostalAddress",
    "ComputerLanguage",
    "VersionedLanguage",
    "PropertyValue",
}


def _reject_known_non_creative_work(value):
    """Reject known non-CreativeWork nodes without inspecting nested values."""

    values = value if isinstance(value, list) else [value]
    for item in values:
        if isinstance(item, dict):
            types = {
                type_name
                for type_name in (item.get("@type"), item.get("type"))
                if isinstance(type_name, str)
            }
        else:
            types = {getattr(item, "type", None)}
        known_type = next(
            (type_name for type_name in types if type_name in _NON_CREATIVE_WORK_TYPES),
            None,
        )
        if known_type is not None:
            raise ValueError(
                f"{known_type} is not valid in a CreativeWork relationship field"
            )
    return value
# ---------------------------------------------------------------------------
# Simple types
# ---------------------------------------------------------------------------


class ContactPoint(Thing):
    """A schema.org contact point."""

    type: Literal["ContactPoint"] = Field("ContactPoint", alias="@type")
    contactType: str | None = None
    email: str | None = None


class PostalAddress(Thing):
    """A schema.org postal address."""

    type: Literal["PostalAddress"] = Field("PostalAddress", alias="@type")
    streetAddress: str | None = None
    addressLocality: str | None = None
    addressRegion: str | None = None
    postalCode: str | None = None
    addressCountry: str | None = None


class Organization(Thing):
    """A schema.org organization."""

    type: Literal["Organization"] = Field("Organization", alias="@type")
    email: str | None = None
    contactPoint: ContactPoint | list[ContactPoint] | None = None
    address: PostalAddress | str | None = None


class Person(Thing):
    """A schema.org person."""

    type: Literal["Person"] = Field("Person", alias="@type")
    email: str | None = None
    affiliation: Organization | str | None = None
    contactPoint: ContactPoint | list[ContactPoint] | None = None
    address: PostalAddress | str | None = None


class Role(Thing):
    """A schema.org role associating an agent with a role description."""

    type: Literal["Role"] = Field("Role", alias="@type")
    roleName: str | None = None
    startDate: date | str | None = None
    endDate: date | str | None = None
    author: Person | Organization | str | None = None

    @field_validator("startDate", "endDate", mode="before")
    @classmethod
    def parse_role_dates(cls, value: date | str | None) -> date | str | None:
        """Convert valid ISO date strings to ``date`` objects."""

        return _parse_iso_date(value)


class ComputerLanguage(Thing):
    """A schema.org computer programming language."""

    type: Literal["ComputerLanguage"] = Field("ComputerLanguage", alias="@type")


class VersionedLanguage(ComputerLanguage):
    """A ComputerLanguage extended with a version field."""

    type: Literal["VersionedLanguage"] = Field("VersionedLanguage", alias="@type")
    version: str | None = None


# Type aliases for agent-style fields (author, contributor, maintainer, etc.).
Agent: TypeAlias = Person | Organization | Role | str
AgentField: TypeAlias = Agent | list[Agent]


# ---------------------------------------------------------------------------
# CreativeWork and subtypes
# ---------------------------------------------------------------------------


class CreativeWork(Thing):
    """A schema.org CreativeWork — base for software, articles, reviews, etc."""

    type: str = Field("CreativeWork", alias="@type")
    author: AgentField | None = None
    contributor: AgentField | None = None
    maintainer: AgentField | None = None
    creator: AgentField | None = None
    editor: Person | list[Person] | None = None
    publisher: Organization | Person | str | list[str] | None = None
    copyrightHolder: AgentField | None = None
    copyrightYear: int | list[int] | None = None
    funder: AgentField | None = None
    sponsor: AgentField | None = None
    provider: AgentField | None = None
    producer: AgentField | None = None
    license: CreativeWork | str | list[CreativeWork | str] | None = None
    citation: ScholarlyArticle | CreativeWork | str | list[ScholarlyArticle | CreativeWork | str] | None = None
    review: Review | str | None = None
    isPartOf: CreativeWork | str | list[CreativeWork | str] | None = None
    hasPart: CreativeWork | str | list[CreativeWork | str] | None = None
    encoding: MediaObject | list[MediaObject] | None = None
    keywords: str | list[str] | None = None
    position: int | str | list[int | str] | None = None
    dateCreated: date | str | None = None
    dateModified: date | str | None = None
    datePublished: date | str | None = None
    supportingData: DataFeed | list[DataFeed] | None = None

    @field_validator("dateCreated", "dateModified", "datePublished", mode="before")
    @classmethod
    def parse_dates(cls, value: date | str | None) -> date | str | None:
        """Convert valid ISO date strings to ``date`` objects."""

        return _parse_iso_date(value)

    @field_validator("license", "citation", "isPartOf", "hasPart", mode="before")
    @classmethod
    def validate_creative_work_relationship(cls, value):
        return _reject_known_non_creative_work(value)


class MediaObject(CreativeWork):
    """A schema.org media object (e.g. for encoding)."""

    type: Literal["MediaObject"] = Field("MediaObject", alias="@type")
    contentUrl: str | None = None
    encodingFormat: str | None = None
    contentSize: str | None = None


class DataFeed(CreativeWork):
    """A schema.org data feed (e.g. for supportingData)."""

    type: Literal["DataFeed"] = Field("DataFeed", alias="@type")
    dataFeedElement: str | None = None


class Review(CreativeWork):
    """A schema.org review."""

    type: Literal["Review"] = Field("Review", alias="@type")
    reviewBody: str | None = None
    reviewAspect: str | None = None


class ScholarlyArticle(CreativeWork):
    """A schema.org scholarly article (e.g. for referencePublication)."""

    type: Literal["ScholarlyArticle"] = Field("ScholarlyArticle", alias="@type")


# ---------------------------------------------------------------------------
# Software types
# ---------------------------------------------------------------------------


class SoftwareSourceCode(CreativeWork):
    """A minimal schema.org SoftwareSourceCode model."""

    context: str | None = Field(None, alias="@context")
    type: Literal["SoftwareSourceCode"] = Field("SoftwareSourceCode", alias="@type")
    codeRepository: str | None = None
    programmingLanguage: VersionedLanguage | ComputerLanguage | str | list[VersionedLanguage | ComputerLanguage | str] | None = None
    runtimePlatform: str | list[str] | None = None
    targetProduct: SoftwareApplication | str | list[SoftwareApplication | str] | None = None
    applicationCategory: str | list[str] | None = None
    applicationSubCategory: str | list[str] | None = None
    downloadUrl: str | list[str] | None = None
    fileSize: str | None = None
    installUrl: str | list[str] | None = None
    memoryRequirements: str | list[str] | None = None
    operatingSystem: str | list[str] | None = None
    permissions: str | list[str] | None = None
    processorRequirements: str | list[str] | None = None
    releaseNotes: str | list[str] | None = None
    softwareHelp: CreativeWork | str | list[CreativeWork | str] | None = None
    softwareRequirements: SoftwareSourceCode | str | list[SoftwareSourceCode | str] | None = None
    softwareVersion: str | None = None
    storageRequirements: str | list[str] | None = None
    fileFormat: str | list[str] | None = None
    isAccessibleForFree: bool | None = None
    relatedLink: str | list[str] | None = None
    version: int | float | str | list[int | float | str] | None = None
    # CodeMeta-specific terms
    buildInstructions: str | list[str] | None = None
    contIntegration: str | list[str] | None = None
    continuousIntegration: str | list[str] | None = None
    developmentStatus: str | None = None
    embargoDate: date | str | None = None
    embargoEndDate: date | str | None = None
    funding: str | list[str] | None = None
    hasSourceCode: SoftwareSourceCode | str | list[SoftwareSourceCode | str] | None = None
    isSourceCodeOf: SoftwareApplication | str | list[SoftwareApplication | str] | None = None
    issueTracker: str | list[str] | None = None
    readme: str | list[str] | None = None
    referencePublication: ScholarlyArticle | str | list[ScholarlyArticle | str] | None = None
    softwareSuggestions: SoftwareSourceCode | str | list[SoftwareSourceCode | str] | None = None

    @field_validator("softwareHelp", mode="before")
    @classmethod
    def validate_software_help_type(cls, value):
        return _reject_known_non_creative_work(value)

    @field_validator("embargoDate", "embargoEndDate", mode="before")
    @classmethod
    def parse_embargo_dates(cls, value: date | str | None) -> date | str | None:
        """Convert valid ISO date strings to ``date`` objects."""

        return _parse_iso_date(value)


class SoftwareApplication(CreativeWork):
    """A schema.org SoftwareApplication model."""

    type: Literal["SoftwareApplication"] = Field("SoftwareApplication", alias="@type")
    applicationCategory: str | list[str] | None = None
    applicationSubCategory: str | list[str] | None = None
    operatingSystem: str | list[str] | None = None
    softwareVersion: str | None = None
    downloadUrl: str | list[str] | None = None
    installUrl: str | list[str] | None = None
    memoryRequirements: str | list[str] | None = None
    processorRequirements: str | list[str] | None = None
    storageRequirements: str | list[str] | None = None
    permissions: str | list[str] | None = None


# ---------------------------------------------------------------------------
# Rebuild models with forward references resolved
# ---------------------------------------------------------------------------


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
VersionedLanguage.model_rebuild()
