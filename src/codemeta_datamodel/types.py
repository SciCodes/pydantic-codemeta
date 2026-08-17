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


# Type alias for agent-style fields (author, contributor, maintainer).
Agent: TypeAlias = Person | Organization | Role | str
AgentField: TypeAlias = Agent | list[Agent]


# ---------------------------------------------------------------------------
# CreativeWork and subtypes
# ---------------------------------------------------------------------------


class CreativeWork(Thing):
    """A schema.org CreativeWork — base for software, articles, reviews, etc."""

    type: Literal["CreativeWork"] = Field("CreativeWork", alias="@type")
    author: AgentField | None = None
    contributor: AgentField | None = None
    maintainer: AgentField | None = None
    publisher: Organization | Person | str | None = None
    funder: Organization | Person | str | None = None
    sponsor: Organization | Person | str | None = None
    provider: Organization | Person | str | None = None
    producer: Organization | Person | str | None = None
    license: CreativeWork | str | None = None
    citation: CreativeWork | ScholarlyArticle | str | None = None
    review: Review | str | None = None
    keywords: str | list[str] | None = None
    dateCreated: date | str | None = None
    dateModified: date | str | None = None
    datePublished: date | str | None = None
    supportingData: DataFeed | list[DataFeed] | None = None

    @field_validator("dateCreated", "dateModified", "datePublished", mode="before")
    @classmethod
    def parse_dates(cls, value: date | str | None) -> date | str | None:
        """Convert valid ISO date strings to ``date`` objects."""

        return _parse_iso_date(value)


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
    programmingLanguage: ComputerLanguage | str | list[ComputerLanguage | str] | None = None
    softwareRequirements: str | None = None
    runtimePlatform: str | None = None
    operatingSystem: str | None = None
    memoryRequirements: str | None = None
    processorRequirements: str | None = None
    storageRequirements: str | None = None
    softwareHelp: str | None = None
    targetProduct: str | None = None
    downloadUrl: str | None = None
    installUrl: str | None = None
    relatedLink: str | None = None
    version: str | None = None
    # CodeMeta-specific terms
    buildInstructions: str | None = None
    contIntegration: str | None = None
    continuousIntegration: str | None = None
    developmentStatus: str | None = None
    embargoDate: date | str | None = None
    embargoEndDate: date | str | None = None
    funding: str | None = None
    hasSourceCode: str | None = None
    isSourceCodeOf: str | None = None
    issueTracker: str | None = None
    readme: str | None = None
    referencePublication: ScholarlyArticle | str | list[ScholarlyArticle | str] | None = None
    softwareSuggestions: str | None = None

    @field_validator("embargoDate", "embargoEndDate", mode="before")
    @classmethod
    def parse_embargo_dates(cls, value: date | str | None) -> date | str | None:
        """Convert valid ISO date strings to ``date`` objects."""

        return _parse_iso_date(value)


class SoftwareApplication(CreativeWork):
    """A schema.org SoftwareApplication model."""

    type: Literal["SoftwareApplication"] = Field("SoftwareApplication", alias="@type")
    applicationCategory: str | None = None
    operatingSystem: str | None = None
    softwareVersion: str | None = None
    downloadUrl: str | None = None
    installUrl: str | None = None


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
