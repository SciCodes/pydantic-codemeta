"""Shared base models for schema.org resources."""

from __future__ import annotations

import json as _json
from typing import Any, Literal, cast

import yaml
from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Self


class SchemaOrgBase(BaseModel):
    """Common JSON-LD behavior for schema.org resources."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",
        use_enum_values=True,
    )

    id: str | None = Field(None, alias="@id")
    type: str = Field(..., alias="@type")

    def to_jsonld(self) -> dict[str, object]:
        """Serialize the model using JSON-LD aliases."""

        return cast(
            dict[str, object],
            self.model_dump(
                by_alias=True,
                exclude_none=True,
                mode="json",
            ),
        )

    @classmethod
    def from_jsonld(cls, data: dict[str, object]) -> Self:
        """Parse a JSON-LD dictionary into a model instance."""

        return cls.model_validate(data)

    def dict(self, serialize: bool = False) -> dict[str, Any]:
        """Return a dictionary representation of the object.

        If serialize is False, this may include unserializable objects like
        datetimes. If serialize is True, returns a JSON-serializable dict.
        """

        if serialize:
            return _json.loads(self.json())
        return self.model_dump(by_alias=True, exclude_none=True)

    def json(self) -> str:
        """Return a serialized JSON string representation of the object."""

        return self.model_dump_json(by_alias=True, exclude_none=True)

    def yaml(self) -> str:
        """Return a serialized YAML string representation of the object."""

        return yaml.dump(
            _json.loads(self.json()),
            sort_keys=False,
            default_flow_style=False,
        )


class Thing(SchemaOrgBase):
    """Base schema.org Thing model."""

    type: Literal["Thing"] = Field("Thing", alias="@type")
    name: str | None = None
    description: str | None = None
    url: str | list[str] | None = None
    identifier: str | PropertyValue | list[str | PropertyValue] | None = None
    sameAs: str | list[str] | None = None


class PropertyValue(Thing):
    """A schema.org structured property value."""

    type: Literal["PropertyValue"] = Field("PropertyValue", alias="@type")
    value: str | int | float | None = None
    propertyID: str | None = None
