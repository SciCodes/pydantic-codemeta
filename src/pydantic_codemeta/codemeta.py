"""CodeMeta v3 models and explicit compatibility adapters."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from .base import JsonLdContext
from .normalization import migrate_legacy_codemeta, normalize_jsonld_context
from .types import SoftwareSourceCode

CODEMETA_V3_CONTEXT = "https://w3id.org/codemeta/3.0"


class CodeMeta(SoftwareSourceCode):
    """Canonical open CodeMeta model preserving any declared context.

    ``from_jsonld`` is a pure parse (``model_validate``) identical to every
    other model. It preserves the declared ``@context`` structure and performs
    no migration or normalization.

    For legacy input that uses prefix-qualified keys (``schema:name``) or
    pre-v3 property names (``creator``, ``embargoDate``,
    ``contIntegration``), use :meth:`from_legacy_jsonld`.
    """

    context: JsonLdContext = Field(CODEMETA_V3_CONTEXT, alias="@context")
    type: Literal["SoftwareSourceCode"] = Field(
        "SoftwareSourceCode", alias="@type"
    )

    @classmethod
    def from_legacy_jsonld(cls, data: dict[str, object]) -> CodeMeta:
        """Parse legacy JSON-LD with prefix flattening and property migration.

        Applies :func:`normalize_jsonld_context` (flattens dict ``@context``
        prefixes, removes the dict context) and :func:`migrate_legacy_codemeta`
        (renames ``creator``→``author``, ``embargoDate``→``embargoEndDate``,
        ``contIntegration``→``continuousIntegration``), then parses the result
        as CodeMeta v3 and adapts to the canonical open :class:`CodeMeta`.

        This is intentionally lossy: the dict ``@context`` is removed after
        prefix flattening, and the v3 context is backfilled. Use
        :meth:`from_jsonld` when the input is already canonical and no
        migration is needed.
        """

        return codemeta_v3_to_codemeta(CodeMetaV3.from_legacy_jsonld(data))


class CodeMetaV3(CodeMeta):
    """Version-specific CodeMeta v3 binding.

    The context and root type are fixed while inherited vocabulary terms and
    raw JSON extras remain open. Direct validation performs no transforms.
    """

    context: Literal[CODEMETA_V3_CONTEXT] = Field(
        CODEMETA_V3_CONTEXT, alias="@context"
    )

    @classmethod
    def from_legacy_jsonld(cls, data: dict[str, object]) -> CodeMetaV3:
        """Normalize and migrate legacy input into the v3 binding."""

        normalized = normalize_jsonld_context(data)
        migrated = migrate_legacy_codemeta(normalized)
        return cls.model_validate(migrated)


def codemeta_v3_to_codemeta(model: CodeMetaV3) -> CodeMeta:
    """Adapt a v3 model to the canonical open CodeMeta model."""

    return CodeMeta.model_validate(model.model_dump(by_alias=True, mode="python"))


def codemeta_to_codemeta_v3(model: CodeMeta) -> CodeMetaV3:
    """Adapt canonical CodeMeta to v3, rejecting non-v3 declared contexts.

    A structured ``@context`` or any string other than the v3 context is
    rejected, since :class:`CodeMetaV3` requires a literal v3 context.
    """

    payload = model.model_dump(by_alias=True, mode="python")
    context = payload.get("@context")
    if context is None:
        payload["@context"] = CODEMETA_V3_CONTEXT
    elif context != CODEMETA_V3_CONTEXT:
        raise ValueError(
            f"CodeMeta context must be {CODEMETA_V3_CONTEXT!r} for v3 adaptation"
        )
    return CodeMetaV3.model_validate(payload)
