"""CodeMeta v3 models and explicit compatibility adapters."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .normalization import migrate_legacy_codemeta, normalize_jsonld_context
from .types import SoftwareSourceCode

CODEMETA_V3_CONTEXT = "https://w3id.org/codemeta/3.0"


class CodeMetaV3(SoftwareSourceCode):
    """Typed/open CodeMeta v3 envelope for ``SoftwareSourceCode`` JSON-LD.

    Inherited fields and extras remain open; this is not an exhaustive
    vocabulary checker. Direct validation performs no input normalization.
    """

    context: Literal[CODEMETA_V3_CONTEXT] = Field(
        CODEMETA_V3_CONTEXT, alias="@context"
    )
    type: Literal["SoftwareSourceCode"] = Field(
        "SoftwareSourceCode", alias="@type"
    )


class CodeMeta(SoftwareSourceCode):
    """Canonical open CodeMeta model preserving any declared string context.

    Direct construction and ``model_validate`` perform no migrations. For
    one-release legacy ingestion, :meth:`from_jsonld` explicitly normalizes
    and migrates input before parsing it as CodeMeta v3.
    """

    context: str | None = Field(CODEMETA_V3_CONTEXT, alias="@context")
    type: Literal["SoftwareSourceCode"] = Field(
        "SoftwareSourceCode", alias="@type"
    )

    @classmethod
    def from_jsonld(cls, data: dict[str, object]) -> CodeMeta:
        """Compatibility shim: normalize and migrate one legacy JSON-LD input."""

        normalized = normalize_jsonld_context(data)
        migrated = migrate_legacy_codemeta(normalized)
        return codemeta_v3_to_codemeta(CodeMetaV3.model_validate(migrated))


def codemeta_v3_to_codemeta(model: CodeMetaV3) -> CodeMeta:
    """Adapt a v3 model to the canonical open CodeMeta model."""

    return CodeMeta.model_validate(model.model_dump(by_alias=True, mode="python"))


def codemeta_to_codemeta_v3(model: CodeMeta) -> CodeMetaV3:
    """Adapt canonical CodeMeta to v3, rejecting non-v3 declared contexts."""

    payload = model.model_dump(by_alias=True, mode="python")
    context = payload.get("@context")
    if context is None:
        payload["@context"] = CODEMETA_V3_CONTEXT
    elif context != CODEMETA_V3_CONTEXT:
        raise ValueError(
            f"CodeMeta context must be {CODEMETA_V3_CONTEXT!r} for v3 adaptation"
        )
    return CodeMetaV3.model_validate(payload)
