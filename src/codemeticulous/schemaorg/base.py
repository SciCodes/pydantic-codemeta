"""Shared base models for schema.org resources."""

from __future__ import annotations

from typing import Literal, cast

from pydantic import BaseModel, ConfigDict, Field


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
    def from_jsonld(cls, data: dict[str, object]) -> SchemaOrgBase:
        """Parse a JSON-LD dictionary into a model instance."""

        return cls.model_validate(data)


class Thing(SchemaOrgBase):
    """Base schema.org Thing model."""

    type: Literal["Thing"] = Field("Thing", alias="@type")
    name: str | None = None
    description: str | None = None
    url: str | None = None
    identifier: str | PropertyValue | list[str | PropertyValue] | None = None


class PropertyValue(Thing):
    """A schema.org structured property value."""

    type: Literal["PropertyValue"] = Field("PropertyValue", alias="@type")
    value: str | int | float | None = None
    propertyID: str | None = None
