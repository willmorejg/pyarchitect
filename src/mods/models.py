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
import json
import uuid
from enum import Enum
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import model_validator
from sqlalchemy import Boolean, Column, String
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
    """A model representing a key-value property (no associated database table; a column value)."""

    key: str
    value: Any


class PydanticListJSON(TypeDecorator):
    """Custom type to serialize list of Pydantic models to JSON."""

    impl = JSON
    cache_ok = True

    @property
    def python_type(self) -> type:
        """Return the Python type object expected for values of this type."""
        return list

    def process_literal_param(self, value: list | None, dialect: Any) -> str:  # noqa: ARG002
        """Process a literal parameter value for inline rendering in SQL.

        Convert PropertyModel instances to dicts before storing.

        Args:
            value: The value to be processed.
            dialect: The SQL dialect in use.

        Returns:
            The processed value as a JSON string.
        """
        if value is None:
            return json.dumps(None)
        processed = [
            item.model_dump() if hasattr(item, "model_dump") else item for item in value
        ]
        return json.dumps(processed)

    def process_bind_param(self, value: list | None, dialect: Any) -> list | None:
        """Convert PropertyModel instances to dicts before storing.

        Args:
            value: The value to be processed.
            dialect: The SQL dialect in use.

        Returns:
            The processed value.
        """
        if value is None:
            return value
        return [
            item.model_dump() if hasattr(item, "model_dump") else item for item in value
        ]

    def process_result_value(self, value: list | None, dialect: Any) -> list | None:
        """Return raw list from database (rehydration happens via model_validator).

        Args:
            value: The value retrieved from the database.
            dialect: The SQL dialect in use.

        Returns:
            The raw value.
        """
        return value


class ConfigurationItem(SQLModel):
    """Base model representing a configuration item in the system."""

    name: str
    description: str | None = None
    model_type: ModelType
    revision: int = 1
    is_active: bool = True
    tags: list[str] = Field(default_factory=list, sa_type=JSON)
    properties: list[PropertyModel] = Field(
        default_factory=list, sa_type=PydanticListJSON
    )
    created: dt.datetime = Field(default_factory=lambda: dt.datetime.now(TIMEZONE))
    created_by: str = "system"
    last_modified: dt.datetime = Field(
        default_factory=lambda: dt.datetime.now(TIMEZONE)
    )
    modified_by: str = "system"

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

        Args:
            key: The property key.
            value: The property value.
        """
        self.properties.append(PropertyModel(key=key, value=value))

    def get_property(self, key: str) -> Any | None:
        """Retrieves a property value by key.

        Args:
            key: The property key.

        Returns:
            The property value or None if not found.
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
        """Get the timezone used by the ConfigurationItem model.

        Returns:
            The ZoneInfo object representing the timezone.
        """
        return TIMEZONE

    def __str__(self) -> str:
        """Return the JSON representation of the model.

        Returns:
            JSON string of the model.
        """
        return self.model_dump_json()


class HardwareItem(ConfigurationItem, table=True):
    """Model representing a hardware configuration item."""

    __tablename__: str = "hardware_items"  # type: ignore[assignment]
    __table_args__ = {"extend_existing": True}

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(String(36), primary_key=True),
    )
    model_type: ModelType = Field(
        default=ModelType.HARDWARE, sa_column=Column(String, nullable=False)
    )
    hardware_type: str = Field(sa_column=Column(String, nullable=False))
    is_cloud: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    hardware_vendor: str = Field(sa_column=Column(String, nullable=False))


class SoftwareItem(ConfigurationItem, table=True):
    """Model representing a software configuration item."""

    __tablename__: str = "software_items"  # type: ignore[assignment]
    __table_args__ = {"extend_existing": True}

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(String(36), primary_key=True),
    )
    model_type: ModelType = Field(
        default=ModelType.SOFTWARE, sa_column=Column(String, nullable=False)
    )
    software_type: str = Field(sa_column=Column(String, nullable=False))
    is_cloud: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    is_internal: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    software_vendor: str = Field(sa_column=Column(String, nullable=False))


class DatabaseItem(ConfigurationItem, table=True):
    """Model representing a database configuration item."""

    __tablename__: str = "database_items"  # type: ignore[assignment]
    __table_args__ = {"extend_existing": True}

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(String(36), primary_key=True),
    )
    model_type: ModelType = Field(
        default=ModelType.DATABASE, sa_column=Column(String, nullable=False)
    )
    database_instance: str = Field(sa_column=Column(String, nullable=False))
    database_name: str = Field(sa_column=Column(String, nullable=False))
    database_schema: str = Field(sa_column=Column(String, nullable=False))
    is_cloud: bool = Field(default=False, sa_column=Column(Boolean, nullable=False))
    database_vendor: str = Field(sa_column=Column(String, nullable=False))


class ProcessItem(ConfigurationItem, table=True):
    """Model representing a process configuration item."""

    __tablename__: str = "process_items"  # type: ignore[assignment]
    __table_args__ = {"extend_existing": True}

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(String(36), primary_key=True),
    )
    model_type: ModelType = Field(
        default=ModelType.PROCESS, sa_column=Column(String, nullable=False)
    )


class PersonItem(ConfigurationItem, table=True):
    """Model representing a person configuration item."""

    __tablename__: str = "person_items"  # type: ignore[assignment]
    __table_args__ = {"extend_existing": True}

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(String(36), primary_key=True),
    )
    model_type: ModelType = Field(
        default=ModelType.PERSON, sa_column=Column(String, nullable=False)
    )


class ModelTypeProperty(SQLModel, table=True):
    """Model representing properties associated with a specific model type."""

    __tablename__: str = "model_type_properties"  # type: ignore[assignment]

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        sa_column=Column(String(36), primary_key=True),
    )
    model_type: ModelType = Field(sa_column=Column(String, nullable=False))
    property_key: str = Field(sa_column=Column(String, nullable=False))
    property_value: str = Field(sa_column=Column(String, nullable=False))

    def __str__(self) -> str:
        """Return the JSON representation of the model.

        Returns:
            JSON string of the model.
        """
        return self.model_dump_json()
