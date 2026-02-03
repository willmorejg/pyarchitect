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
from mods.logging_config import LoggingConfig
from mods.models import (
    ConfigurationItem,
    DatabaseItem,
    HardwareItem,
    ModelType,
    ModelTypeProperty,
    PersonItem,
    ProcessItem,
    SoftwareItem,
)

logger = LoggingConfig().logger


class TestModels:
    """Test suite for models.py."""

    def test_model_type_enum(self):
        """Test the ModelType enum."""
        logger.info("Starting test_model_type_enum")

        assert ModelType.HARDWARE.value == "hardware"
        assert ModelType.SOFTWARE.value == "software"
        assert ModelType.DATABASE.value == "database"
        assert ModelType.PROCESS.value == "process"
        assert ModelType.PERSON.value == "person"

        logger.info("Completed test_model_type_enum successfully")

    def test_configuration_item(self):
        """Test the ConfigurationItem creation and attributes."""
        logger.info("Starting test_configuration_item")

        # set up test values
        name = "Test Model"
        model_type = ModelType.SOFTWARE
        properties = []
        properties.append({"cpu": "Intel i7"})
        properties.append({"ram": "16GB"})
        properties.append({"os": "Ubuntu 22.04"})

        # Create ConfigurationItem instance
        model = ConfigurationItem(
            name=name,
            model_type=model_type,
        )

        for prop in properties:
            for key, value in prop.items():
                model.add_property(key, value)

        # Validate model attributes
        assert model.name == name
        assert model.model_type == model_type
        assert model.is_active is True
        assert model.revision == 1
        assert model.tags == []
        assert len(model.properties) == len(properties)
        for prop in properties:
            for key, value in prop.items():
                assert model.get_property(key) == value
        # just for added verification
        assert model.get_property("cpu") == "Intel i7"

        logger.info("Created ConfigurationItem:", model=str(model))
        logger.info("Completed test_configuration_item successfully")

    def test_model_type_property(self):
        """Test the ModelTypeProperty creation and attributes."""
        logger.info("Starting test_model_type_property")

        model_type = ModelType.DATABASE
        property_key = "environment"
        property_value = "production"

        model_type_property = ModelTypeProperty(
            model_type=model_type,
            property_key=property_key,
            property_value=property_value,
        )

        assert model_type_property.model_type == model_type
        assert model_type_property.property_key == property_key
        assert model_type_property.property_value == property_value
        logger.info("Created ModelTypeProperty:", model=str(model_type_property))
        logger.info("Completed test_model_type_property successfully")

    def test_hardware_item(self):
        """Test the HardwareItem creation and attributes."""
        logger.info("Starting test_hardware_item")

        name = "Production Server"
        hardware_type = "server"
        is_cloud = False
        hardware_vendor = "Dell"

        hardware_item = HardwareItem(
            name=name,
            hardware_type=hardware_type,
            is_cloud=is_cloud,
            hardware_vendor=hardware_vendor,
        )

        # Validate inherited attributes
        assert hardware_item.name == name
        assert hardware_item.model_type == ModelType.HARDWARE
        assert hardware_item.is_active is True
        assert hardware_item.revision == 1
        assert hardware_item.tags == []

        # Validate HardwareItem-specific attributes
        assert hardware_item.hardware_type == hardware_type
        assert hardware_item.is_cloud == is_cloud
        assert hardware_item.hardware_vendor == hardware_vendor

        logger.info("Created HardwareItem:", model=str(hardware_item))
        logger.info("Completed test_hardware_item successfully")

    def test_software_item(self):
        """Test the SoftwareItem creation and attributes."""
        logger.info("Starting test_software_item")

        name = "Web Application"
        software_type = "application"
        is_cloud = True
        is_internal = True
        software_vendor = "Internal Development"

        software_item = SoftwareItem(
            name=name,
            software_type=software_type,
            is_cloud=is_cloud,
            is_internal=is_internal,
            software_vendor=software_vendor,
        )

        # Validate inherited attributes
        assert software_item.name == name
        assert software_item.model_type == ModelType.SOFTWARE
        assert software_item.is_active is True
        assert software_item.revision == 1
        assert software_item.tags == []

        # Validate SoftwareItem-specific attributes
        assert software_item.software_type == software_type
        assert software_item.is_cloud == is_cloud
        assert software_item.is_internal == is_internal
        assert software_item.software_vendor == software_vendor

        logger.info("Created SoftwareItem:", model=str(software_item))
        logger.info("Completed test_software_item successfully")

    def test_database_item(self):
        """Test the DatabaseItem creation and attributes."""
        logger.info("Starting test_database_item")

        name = "Production Database"
        model_type = ModelType.DATABASE
        database_instance = "prod-db-01"
        database_name = "production_db"
        database_schema = "public"
        is_cloud = True
        database_vendor = "PostgreSQL"

        database_item = DatabaseItem(
            name=name,
            model_type=model_type,
            database_instance=database_instance,
            database_name=database_name,
            database_schema=database_schema,
            is_cloud=is_cloud,
            database_vendor=database_vendor,
        )

        # Validate inherited attributes
        assert database_item.name == name
        assert database_item.model_type == model_type
        assert database_item.is_active is True
        assert database_item.revision == 1
        assert database_item.tags == []

        # Validate DatabaseItem-specific attributes
        assert database_item.database_instance == database_instance
        assert database_item.database_name == database_name
        assert database_item.database_schema == database_schema
        assert database_item.is_cloud == is_cloud
        assert database_item.database_vendor == database_vendor

        logger.info("Created DatabaseItem:", model=str(database_item))
        logger.info("Completed test_database_item successfully")

    def test_process_item(self):
        """Test the ProcessItem creation and attributes."""
        logger.info("Starting test_process_item")

        name = "Data Pipeline"

        process_item = ProcessItem(
            name=name,
        )

        # Validate inherited attributes
        assert process_item.name == name
        assert process_item.model_type == ModelType.PROCESS
        assert process_item.is_active is True
        assert process_item.revision == 1
        assert process_item.tags == []

        logger.info("Created ProcessItem:", model=str(process_item))
        logger.info("Completed test_process_item successfully")

    def test_person_item(self):
        """Test the PersonItem creation and attributes."""
        logger.info("Starting test_person_item")

        name = "John Doe"

        person_item = PersonItem(
            name=name,
        )

        # Validate inherited attributes
        assert person_item.name == name
        assert person_item.model_type == ModelType.PERSON
        assert person_item.is_active is True
        assert person_item.revision == 1
        assert person_item.tags == []

        logger.info("Created PersonItem:", model=str(person_item))
        logger.info("Completed test_person_item successfully")
