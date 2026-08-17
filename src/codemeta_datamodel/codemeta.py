"""CodeMeta convenience wrapper models."""

from __future__ import annotations

from typing import Literal

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
    type: Literal["SoftwareSourceCode"] = Field(
        "SoftwareSourceCode",
        alias="@type",
    )

    @model_validator(mode="after")
    def validate_wrapper_defaults(self) -> CodeMeta:
        """Keep the wrapper's JSON-LD context and type fixed by default."""

        context_default = type(self).model_fields["context"].default
        type_default = type(self).model_fields["type"].default

        if self.context != context_default:
            raise ValueError(f"CodeMeta context must be {context_default!r}.")
        if self.type != type_default:
            raise ValueError(f"CodeMeta type must be {type_default!r}.")

        return self
