"""Shared JSON-LD behavior and base schema.org models."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Literal, TypeAlias, cast

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator
from typing_extensions import Self


JsonLdContextObject: TypeAlias = dict[str, JsonValue]
JsonLdContextEntry: TypeAlias = str | JsonLdContextObject | None
JsonLdContext: TypeAlias = JsonLdContextEntry | list[JsonLdContextEntry]


class SchemaOrgBase(BaseModel):
    """Common JSON-LD behavior for the package's typed resources.

    Declared fields are typed vocabulary terms. Extra fields are retained as
    raw JSON-compatible values so future terms and extensions can round-trip.
    """

    model_config = ConfigDict(
        allow_inf_nan=False,
        populate_by_name=True,
        extra="allow",
        use_enum_values=True,
    )

    __pydantic_extra__: dict[str, JsonValue] = Field(init=False)

    id: str | None = Field(None, alias="@id")
    type: str = Field(..., alias="@type")

    @model_validator(mode="before")
    @classmethod
    def reject_alias_name_collisions(cls, data: object) -> object:
        """Reject ambiguous input containing both a field name and its alias."""

        if not isinstance(data, Mapping):
            return data

        collisions = [
            (name, field.alias)
            for name, field in cls.model_fields.items()
            if isinstance(field.alias, str)
            and field.alias != name
            and name in data
            and field.alias in data
        ]
        if collisions:
            rendered = ", ".join(
                f"{name!r} and {alias!r}" for name, alias in collisions
            )
            raise ValueError(f"Conflicting field name and JSON-LD alias: {rendered}")
        return data

    def to_jsonld(self) -> dict[str, object]:
        """Serialize the model using JSON-LD aliases."""

        payload = cast(
            dict[str, object],
            self.model_dump(
                by_alias=True,
                mode="json",
            ),
        )
        return cast(dict[str, object], _prune_declared_none(self, payload))

    @classmethod
    def from_jsonld(cls, data: dict[str, object]) -> Self:
        """Validate a JSON-LD dictionary without normalization or migration."""

        return cls.model_validate(data)


def _prune_declared_none(value: object, serialized: object) -> object:
    """Omit null typed fields while retaining nulls inside raw JSON extras."""

    if isinstance(value, SchemaOrgBase) and isinstance(serialized, dict):
        for name, field in type(value).model_fields.items():
            alias = field.serialization_alias or field.alias or name
            field_value = getattr(value, name)
            if field_value is None:
                preserve_null_context = (
                    name == "context" and name in value.model_fields_set
                )
                if not preserve_null_context:
                    serialized.pop(alias, None)
            elif alias in serialized:
                serialized[alias] = _prune_declared_none(
                    field_value, serialized[alias]
                )
        return serialized
    if isinstance(value, list) and isinstance(serialized, list):
        return [
            _prune_declared_none(item, dumped)
            for item, dumped in zip(value, serialized, strict=True)
        ]
    return serialized


class Thing(SchemaOrgBase):
    """Base schema.org Thing model."""

    type: Literal["Thing"] = Field("Thing", alias="@type")
    name: str | None = None
    description: str | None = None
    url: str | list[str] | None = None
    identifier: str | PropertyValue | list[str | PropertyValue] | None = None
    related_link: str | list[str] | None = Field(None, alias="relatedLink")
    same_as: str | list[str] | None = Field(None, alias="sameAs")


class PropertyValue(Thing):
    """A schema.org structured property value."""

    type: Literal["PropertyValue"] = Field("PropertyValue", alias="@type")
    value: str | int | float | None = None
    property_id: str | None = Field(None, alias="propertyID")
