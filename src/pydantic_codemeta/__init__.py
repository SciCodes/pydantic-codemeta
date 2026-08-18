"""Minimal schema.org models used for CodeMeta metadata."""

from .base import PropertyValue, SchemaOrgBase, Thing
from .codemeta import (
    CODEMETA_V3_CONTEXT,
    CodeMeta,
    CodeMetaV3,
    codemeta_to_codemeta_v3,
    codemeta_v3_to_codemeta,
)
from .normalization import migrate_legacy_codemeta, normalize_jsonld_context
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
    VersionedLanguage,
)

__all__ = [
    "CodeMeta",
    "CodeMetaV3",
    "CODEMETA_V3_CONTEXT",
    "codemeta_v3_to_codemeta",
    "codemeta_to_codemeta_v3",
    "normalize_jsonld_context",
    "migrate_legacy_codemeta",
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
    "VersionedLanguage",
]
