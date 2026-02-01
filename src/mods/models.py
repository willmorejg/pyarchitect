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
from typing import Annotated, Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

TIMEZONE = ZoneInfo("America/New_York")


class ModelType(str, Enum):
    """Model types available in the system."""

    HARDWARE = "hardware"
    SOFTWARE = "software"
    DATABASE = "database"
    PROCESS = "process"
    PERSON = "person"


class PropertyModel(BaseModel):
    """A model representing a key-value property."""

    key: str
    value: Any


class SuperModel(BaseModel):
    """A super model representing a generic entity in the system."""

    id: Annotated[uuid.UUID, Field(default_factory=uuid.uuid4)]
    name: str
    description: str | None = None
    model_type: ModelType
    revision: int = 1
    is_active: bool = True
    tags: Annotated[list[str], Field(default_factory=list)]
    properties: Annotated[list[PropertyModel], Field(default_factory=list)]
    created: Annotated[dt.datetime, Field(default_factory=lambda: dt.datetime.now(TIMEZONE))]
    created_by: str = "system"
    last_modified: Annotated[dt.datetime, Field(default_factory=lambda: dt.datetime.now(TIMEZONE))]
    modified_by: str = "system"

    def add_property(self, key: str, value: Any) -> None:
        """Adds a property to the model.
        :param key: The property key.
        :param value: The property value.
        """
        self.properties.append(PropertyModel(key=key, value=value))

    def __str__(self) -> str:
        return self.model_dump_json()
