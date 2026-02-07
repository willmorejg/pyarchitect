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

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON
from sqlmodel import Column, Field, SQLModel

TIMEZONE = ZoneInfo("America/New_York")
_CI_ID_FK = "configuration_items.id"


class ModelType(str, Enum):
    """Model types available in the system."""

    HARDWARE = "hardware"
    SOFTWARE = "software"
    DATABASE = "database"
    PROCESS = "process"
    PERSON = "person"

class CommunicationType(str, Enum):
    """Communication types for configuration items."""

    API = "api"
    MESSAGE_QUEUE = "message_queue"
    FILE_TRANSFER = "file_transfer"
    OTHER = "other"


class PropertyModel(SQLModel):
    """A model representing a key-value property (no associated database table; a column value)."""

    key: str
    value: Any


class _Base(DeclarativeBase):
    """SQLAlchemy declarative base sharing SQLModel's metadata.

    This enables joined table inheritance for the ConfigurationItem hierarchy
    while coexisting with SQLModel table classes (e.g., ModelTypeProperty).
    """

    metadata = SQLModel.metadata


class ConfigurationItem(_Base):
    """Base model representing a configuration item in the system.

    Uses joined table inheritance: shared columns live in the
    ``configuration_items`` table, and each subclass stores only its
    specific columns in a separate table linked by foreign key.
    """

    __tablename__ = "configuration_items"
    __table_args__ = {"extend_existing": True}
    __mapper_args__ = {
        "polymorphic_on": "model_type",
        "polymorphic_identity": None,
    }

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )
    model_type: Mapped[str] = mapped_column(String, nullable=False)
    revision: Mapped[int] = mapped_column(default=1)
    is_active: Mapped[bool] = mapped_column(default=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    properties: Mapped[list] = mapped_column(JSON, default=list)
    created: Mapped[dt.datetime] = mapped_column(
        default=lambda: dt.datetime.now(TIMEZONE)
    )
    created_by: Mapped[str] = mapped_column(String, default="system")
    last_modified: Mapped[dt.datetime] = mapped_column(
        default=lambda: dt.datetime.now(TIMEZONE)
    )
    modified_by: Mapped[str] = mapped_column(String, default="system")

    outgoing_communications: Mapped[list["ConfigurationItemCommunication"]] = relationship(
        foreign_keys="ConfigurationItemCommunication.source_id",
        lazy="selectin",
    )
    incoming_communications: Mapped[list["ConfigurationItemCommunication"]] = relationship(
        foreign_keys="ConfigurationItemCommunication.target_id",
        lazy="selectin",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with Python-level defaults.

        SQLAlchemy's mapped_column defaults only apply at INSERT time.
        This ensures defaults are available immediately on the Python object.
        """
        _defaults = {
            "id": lambda: str(uuid.uuid4()),
            "revision": lambda: 1,
            "is_active": lambda: True,
            "tags": list,
            "properties": list,
            "created": lambda: dt.datetime.now(TIMEZONE),
            "created_by": lambda: "system",
            "last_modified": lambda: dt.datetime.now(TIMEZONE),
            "modified_by": lambda: "system",
        }
        for key, factory in _defaults.items():
            if key not in kwargs:
                kwargs[key] = factory()
        super().__init__(**kwargs)

    def add_communication(
        self,
        target: "ConfigurationItem",
        communication_type: CommunicationType,
        description: str | None = None,
    ) -> "ConfigurationItemCommunication":
        """Add a communication link from this item to a target item.

        Args:
            target: The target ConfigurationItem.
            communication_type: The type of communication.
            description: Optional description of the communication.

        Returns:
            The created ConfigurationItemCommunication instance.
        """
        comm = ConfigurationItemCommunication(
            source_id=self.id,
            target_id=target.id,
            communication_type=communication_type.value
            if isinstance(communication_type, CommunicationType)
            else communication_type,
            description=description,
        )
        self.outgoing_communications.append(comm)
        return comm

    def get_communications(self) -> list["ConfigurationItemCommunication"]:
        """Get all communications (both incoming and outgoing) for this item.

        Returns:
            Combined list of incoming and outgoing communications.
        """
        return list(self.outgoing_communications) + list(
            self.incoming_communications
        )

    def add_property(self, key: str, value: Any) -> None:
        """Adds a property to the model.

        Args:
            key: The property key.
            value: The property value.
        """
        current = self.properties or []
        self.properties = [*current, {"key": key, "value": value}]

    def get_property(self, key: str) -> Any | None:
        """Retrieves a property value by key.

        Args:
            key: The property key.

        Returns:
            The property value or None if not found.
        """
        for prop in self.properties or []:
            if isinstance(prop, dict):
                if prop.get("key") == key:
                    return prop.get("value")
            elif hasattr(prop, "key") and prop.key == key:
                return prop.value
        return None

    @staticmethod
    def get_timezone() -> ZoneInfo:
        """Get the timezone used by the ConfigurationItem model.

        Returns:
            The ZoneInfo object representing the timezone.
        """
        return TIMEZONE

    def model_dump(self) -> dict[str, Any]:
        """Return a dictionary representation of the model.

        Returns:
            Dictionary of all mapped column values, plus communications.
        """
        result: dict[str, Any] = {}
        for col in self.__class__.__mapper__.columns:
            value = getattr(self, col.key)
            if isinstance(value, Enum):
                value = value.value
            result[col.key] = value
        comms = self.get_communications()
        if comms:
            result["communications"] = [c.model_dump() for c in comms]
        return result

    def model_dump_json(self) -> str:
        """Return a JSON string representation of the model.

        Returns:
            JSON string of the model.
        """
        data = self.model_dump()
        for key, value in data.items():
            if isinstance(value, dt.datetime):
                data[key] = value.isoformat()
        return json.dumps(data)

    def __str__(self) -> str:
        """Return the JSON representation of the model.

        Returns:
            JSON string of the model.
        """
        return self.model_dump_json()


class ConfigurationItemCommunication(_Base):
    """Association table defining communication links between configuration items."""

    __tablename__ = "configuration_item_communications"
    __table_args__ = {"extend_existing": True}

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    source_id: Mapped[str] = mapped_column(
        ForeignKey(_CI_ID_FK), nullable=False
    )
    target_id: Mapped[str] = mapped_column(
        ForeignKey(_CI_ID_FK), nullable=False
    )
    communication_type: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(
        String, nullable=True, default=None
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with Python-level defaults."""
        if "id" not in kwargs:
            kwargs["id"] = str(uuid.uuid4())
        super().__init__(**kwargs)

    def model_dump(self) -> dict[str, Any]:
        """Return a dictionary representation of the communication.

        Returns:
            Dictionary of all mapped column values.
        """
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "communication_type": self.communication_type,
            "description": self.description,
        }


class HardwareItem(ConfigurationItem):
    """Model representing a hardware configuration item."""

    __tablename__ = "hardware_items"
    __table_args__ = {"extend_existing": True}
    __mapper_args__ = {"polymorphic_identity": ModelType.HARDWARE.value}

    id: Mapped[str] = mapped_column(
        ForeignKey(_CI_ID_FK), primary_key=True
    )
    hardware_type: Mapped[str] = mapped_column(String)
    is_cloud: Mapped[bool] = mapped_column(Boolean, default=False)
    hardware_vendor: Mapped[str] = mapped_column(String)


class SoftwareItem(ConfigurationItem):
    """Model representing a software configuration item."""

    __tablename__ = "software_items"
    __table_args__ = {"extend_existing": True}
    __mapper_args__ = {"polymorphic_identity": ModelType.SOFTWARE.value}

    id: Mapped[str] = mapped_column(
        ForeignKey(_CI_ID_FK), primary_key=True
    )
    software_type: Mapped[str] = mapped_column(String)
    is_cloud: Mapped[bool] = mapped_column(Boolean, default=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    software_vendor: Mapped[str] = mapped_column(String)


class DatabaseItem(ConfigurationItem):
    """Model representing a database configuration item."""

    __tablename__ = "database_items"
    __table_args__ = {"extend_existing": True}
    __mapper_args__ = {"polymorphic_identity": ModelType.DATABASE.value}

    id: Mapped[str] = mapped_column(
        ForeignKey(_CI_ID_FK), primary_key=True
    )
    database_instance: Mapped[str] = mapped_column(String)
    database_name: Mapped[str] = mapped_column(String)
    database_schema: Mapped[str] = mapped_column(String)
    is_cloud: Mapped[bool] = mapped_column(Boolean, default=False)
    database_vendor: Mapped[str] = mapped_column(String)


class ProcessItem(ConfigurationItem):
    """Model representing a process configuration item."""

    __tablename__ = "process_items"
    __table_args__ = {"extend_existing": True}
    __mapper_args__ = {"polymorphic_identity": ModelType.PROCESS.value}

    id: Mapped[str] = mapped_column(
        ForeignKey(_CI_ID_FK), primary_key=True
    )


class PersonItem(ConfigurationItem):
    """Model representing a person configuration item."""

    __tablename__ = "person_items"
    __table_args__ = {"extend_existing": True}
    __mapper_args__ = {"polymorphic_identity": ModelType.PERSON.value}

    id: Mapped[str] = mapped_column(
        ForeignKey(_CI_ID_FK), primary_key=True
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
