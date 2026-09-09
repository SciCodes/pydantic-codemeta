"""Shared JSON-LD behavior and base schema.org models."""

from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
from typing import Annotated, Literal, Self, TypeAlias, cast

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    JsonValue,
    StrictBool,
    StrictFloat,
    StrictInt,
    model_validator,
)


def _check_raw_json_value(value: object, path: str) -> None:
    """Reject Python-only values before Pydantic can coerce them."""

    value_type = type(value)
    if value is None or value_type in (bool, int, str):
        return
    if value_type is float:
        if not isfinite(value):
            raise ValueError(f"{path} must contain only finite JSON numbers")
        return
    if value_type is list:
        for index, item in enumerate(value):
            _check_raw_json_value(item, f"{path}[{index}]")
        return
    if value_type is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError(f"{path} must contain only string object keys")
            _check_raw_json_value(item, f"{path}.{key}")
        return
    raise ValueError(f"{path} must be a raw JSON value")


def _validate_raw_json_value(value: object) -> object:
    _check_raw_json_value(value, "$")
    return value


def _declared_input_keys(model: type[BaseModel]) -> set[str]:
    """Return field names and string aliases accepted as declared input."""

    return {
        key
        for name, field in model.model_fields.items()
        for key in (name, field.alias)
        if isinstance(key, str)
    }


RawJsonValue: TypeAlias = Annotated[
    JsonValue, BeforeValidator(_validate_raw_json_value)
]
RawJsonObject: TypeAlias = Annotated[
    dict[str, JsonValue], BeforeValidator(_validate_raw_json_value)
]
JsonLdContextObject: TypeAlias = RawJsonObject
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

    __pydantic_extra__: dict[str, object] = Field(init=False)

    id: str | None = Field(None, alias="@id")
    type: str = Field(..., alias="@type")

    @model_validator(mode="before")
    @classmethod
    def reject_alias_name_collisions(cls, data: object) -> object:
        """Reject ambiguous aliases and Python-only extra values."""

        if not isinstance(data, Mapping):
            return data

        field_keys = _declared_input_keys(cls)
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

        for key, value in data.items():
            if key not in field_keys:
                _check_raw_json_value(value, key)
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
                serialized[alias] = _prune_declared_none(field_value, serialized[alias])
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
    value: StrictBool | str | StrictInt | StrictFloat | RawJsonObject | None = None
    property_id: str | None = Field(None, alias="propertyID")
