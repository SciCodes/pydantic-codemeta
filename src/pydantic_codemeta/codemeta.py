"""CodeMeta convenience wrapper models."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import Field, model_validator

from .types import SoftwareSourceCode


class CodeMeta(SoftwareSourceCode):
    """Convenience wrapper for CodeMeta JSON-LD documents.

    This model is version-locked to CodeMeta 3.0. The ``@context`` and
    ``@type`` fields are fixed and cannot be overridden. To handle other
    CodeMeta versions (e.g. a future v4), use :class:`SoftwareSourceCode`
    directly so the declared ``@context`` is preserved through round-trip
    serialization.
    """

    context: str = Field(
        "https://w3id.org/codemeta/3.0",
        alias="@context",
    )
    type: Literal["SoftwareSourceCode", "SoftwareApplication"] = Field(
        "SoftwareSourceCode",
        alias="@type",
    )

    @model_validator(mode="before")
    @classmethod
    def map_type_and_id(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Map bare ``type``/``id`` keys to ``@type``/``@id`` for convenience."""

        if not isinstance(values, dict):
            return values
        if ("type" in values and "@type" not in values) or (
            "id" in values and "@id" not in values
        ):
            values = dict(values)
            if "type" in values and "@type" not in values:
                values["@type"] = values.pop("type")
            if "id" in values and "@id" not in values:
                values["@id"] = values.pop("id")
        return values

    @model_validator(mode="before")
    @classmethod
    def collapse_jsonld_context(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Flatten JSON-LD context prefixes and strip dict-based ``@context``.

        CodeMeta documents often use a ``@context`` dict with prefix
        mappings (e.g. ``{"schema": "https://schema.org/"}``). This
        validator strips dict-based ``@context`` and removes known
        prefixes from keys so the model sees unprefixed property names.

        String ``@context`` values (e.g. ``"https://w3id.org/codemeta/3.0"``)
        are preserved so that :meth:`validate_wrapper_defaults` can
        reject non-3.0 contexts.
        """

        if not isinstance(values, dict):
            return values
        context = values.get("@context")
        if isinstance(context, dict):
            values = dict(values)
            prefixes = list(context.keys())
            for key in list(values.keys()):
                for prefix in prefixes:
                    if key.startswith(f"{prefix}:"):
                        values[key.removeprefix(f"{prefix}:")] = values.pop(key)
                        break
            values.pop("@context", None)
        return values

    @model_validator(mode="before")
    @classmethod
    def coalesce_embargo_end_date(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Coalesce ``embargoDate`` into ``embargoEndDate`` (removed in v3)."""

        if not isinstance(values, dict):
            return values
        embargo_date = values.get("embargoDate")
        embargo_end_date = values.get("embargoEndDate")
        if embargo_date and embargo_end_date:
            raise ValueError(
                "'embargoDate' field is removed in CodeMeta v3, "
                "use 'embargoEndDate' instead"
            )
        if embargo_date:
            values = dict(values)
            values["embargoEndDate"] = embargo_date
            del values["embargoDate"]
        return values

    @model_validator(mode="before")
    @classmethod
    def coalesce_continuous_integration(
        cls, values: dict[str, Any]
    ) -> dict[str, Any]:
        """Coalesce ``contIntegration`` into ``continuousIntegration``."""

        if not isinstance(values, dict):
            return values
        cont_integration = values.get("contIntegration")
        continuous_integration = values.get("continuousIntegration")
        if cont_integration and continuous_integration:
            raise ValueError(
                "'contIntegration' field is removed in CodeMeta v3, "
                "use 'continuousIntegration' instead"
            )
        if cont_integration:
            values = dict(values)
            values["continuousIntegration"] = cont_integration
            del values["contIntegration"]
        return values

    @model_validator(mode="before")
    @classmethod
    def coalesce_creator_author(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Coalesce ``creator`` into ``author`` (removed in v3)."""

        if not isinstance(values, dict):
            return values
        author = values.get("author")
        creator = values.get("creator")
        if author and creator:
            raise ValueError(
                "'creator' field is removed in CodeMeta v3, "
                "use 'author' instead"
            )
        if creator:
            values = dict(values)
            values["author"] = creator
            del values["creator"]
        return values

    @model_validator(mode="after")
    def validate_wrapper_defaults(self) -> CodeMeta:
        """Keep the wrapper's JSON-LD context fixed to CodeMeta 3.0."""

        context_default = type(self).model_fields["context"].default
        type_default = type(self).model_fields["type"].default

        if self.context != context_default:
            raise ValueError(f"CodeMeta context must be {context_default!r}.")
        if self.type != type_default:
            raise ValueError(f"CodeMeta type must be {type_default!r}.")

        return self
