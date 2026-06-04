"""Concrete schema.org types used by CodeMeta."""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import Field, field_validator

from .base import PropertyValue, Thing


class ContactPoint(Thing):
    """A schema.org contact point."""

    type: Literal["ContactPoint"] = Field("ContactPoint", alias="@type")
    contactType: str | None = None
    email: str | None = None


class Organization(Thing):
    """A schema.org organization."""

    type: Literal["Organization"] = Field("Organization", alias="@type")
    email: str | None = None
    contactPoint: ContactPoint | list[ContactPoint] | None = None


class Person(Thing):
    """A schema.org person."""

    type: Literal["Person"] = Field("Person", alias="@type")
    email: str | None = None
    affiliation: Organization | str | None = None
    contactPoint: ContactPoint | list[ContactPoint] | None = None


class SoftwareSourceCode(Thing):
    """A minimal schema.org SoftwareSourceCode model."""

    context: str | None = Field(None, alias="@context")
    type: Literal["SoftwareSourceCode"] = Field("SoftwareSourceCode", alias="@type")
    author: Person | Organization | str | list[Person | Organization | str] | None = None
    contributor: Person | Organization | str | list[Person | Organization | str] | None = None
    maintainer: Person | Organization | str | list[Person | Organization | str] | None = None
    publisher: Organization | Person | str | None = None
    keywords: str | list[str] | None = None
    license: str | list[str] | None = None
    codeRepository: str | None = None
    programmingLanguage: str | list[str] | None = None
    version: str | None = None
    dateCreated: date | str | None = None
    dateModified: date | str | None = None
    datePublished: date | str | None = None

    @field_validator("dateCreated", "dateModified", "datePublished", mode="before")
    @classmethod
    def parse_iso_dates(cls, value: date | str | None) -> date | str | None:
        """Convert valid ISO date strings to ``date`` objects."""

        if not isinstance(value, str):
            return value

        try:
            return date.fromisoformat(value)
        except ValueError:
            return value


class SoftwareApplication(SoftwareSourceCode):
    """A schema.org SoftwareApplication model."""

    type: Literal["SoftwareApplication"] = Field("SoftwareApplication", alias="@type")
