"""Minimal schema.org models used for CodeMeta metadata."""

from .base import PropertyValue, SchemaOrgBase, Thing
from .codemeta import CodeMeta
from .types import (
    ComputerLanguage,
    ContactPoint,
    CreativeWork,
    DataFeed,
    MediaObject,
    Organization,
    Person,
    PostalAddress,
    Review,
    Role,
    ScholarlyArticle,
    SoftwareApplication,
    SoftwareSourceCode,
)

__all__ = [
    "CodeMeta",
    "ComputerLanguage",
    "ContactPoint",
    "CreativeWork",
    "DataFeed",
    "MediaObject",
    "Organization",
    "Person",
    "PostalAddress",
    "PropertyValue",
    "Review",
    "Role",
    "SchemaOrgBase",
    "ScholarlyArticle",
    "SoftwareApplication",
    "SoftwareSourceCode",
    "Thing",
]
