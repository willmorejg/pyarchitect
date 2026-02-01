# Copyright 2026 James G Willmore
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import datetime as dt
import uuid
from enum import Enum
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import model_validator
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.types import JSON, TypeDecorator
from sqlmodel import Field, SQLModel

TIMEZONE = ZoneInfo("America/New_York")


class ModelType(str, Enum):
    """Model types available in the system."""

    HARDWARE = "hardware"
    SOFTWARE = "software"
    DATABASE = "database"
    PROCESS = "process"
    PERSON = "person"


class PropertyModel(SQLModel):
    """A model representing a key-value property."""

    key: str
    value: Any


class PydanticListJSON(TypeDecorator):
    """Custom type to serialize list of Pydantic models to JSON."""

    impl = JSON
    cache_ok = True

    def process_bind_param(self, value: list | None, dialect: Any) -> list | None:
        """Convert PropertyModel instances to dicts before storing."""
        if value is None:
            return value
        return [item.model_dump() if hasattr(item, "model_dump") else item for item in value]

    def process_result_value(self, value: list | None, dialect: Any) -> list | None:
        """Return raw list from database (rehydration happens via model_validator)."""
        return value


class ConfigurationItem(SQLModel, table=True):
    """Model representing a configuration item in the system."""

    __tablename__: str = "configuration_items"  # type: ignore[assignment]

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(String(36), primary_key=True),
    )
    name: str = Field(sa_column=Column(String, nullable=False))
    description: str | None = Field(default=None, sa_column=Column(String, nullable=True))
    model_type: ModelType = Field(sa_column=Column(String, nullable=False))
    revision: int = Field(default=1, sa_column=Column(Integer, nullable=False))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, nullable=False))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    properties: list[PropertyModel] = Field(
        default_factory=list, sa_column=Column(PydanticListJSON, nullable=False)
    )
    created: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(TIMEZONE),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    created_by: str = Field(default="system", sa_column=Column(String, nullable=False))
    last_modified: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(TIMEZONE),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    modified_by: str = Field(default="system", sa_column=Column(String, nullable=False))

    @model_validator(mode="after")
    def rehydrate_properties(self) -> "ConfigurationItem":
        """Convert dict properties back to PropertyModel instances on load."""
        if self.properties and len(self.properties) > 0:
            first = self.properties[0]
            if isinstance(first, dict):
                self.properties = [
                    PropertyModel(key=p["key"], value=p["value"])  # type: ignore[index]
                    for p in self.properties
                ]
        return self

    def add_property(self, key: str, value: Any) -> None:
        """Adds a property to the model.
        :param key: The property key.
        :param value: The property value.
        """
        self.properties.append(PropertyModel(key=key, value=value))

    def get_property(self, key: str) -> Any | None:
        """Retrieves a property value by key.
        :param key: The property key.
        :return: The property value or None if not found.
        """
        for prop in self.properties:
            # Handle both PropertyModel instances and dicts (from DB load)
            if isinstance(prop, dict):
                if prop.get("key") == key:
                    return prop.get("value")
            elif prop.key == key:
                return prop.value
        return None
    
    @staticmethod
    def get_timezone() -> ZoneInfo:
        """Get the timezone used by the ConfigurationItem model."""
        return TIMEZONE

    def __str__(self) -> str:
        return self.model_dump_json()
