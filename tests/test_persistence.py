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
import os

from mods.logging_config import LoggingConfig
from mods.models import (
    DatabaseItem,
    HardwareItem,
    ModelType,
    ModelTypeProperty,
    PersonItem,
    ProcessItem,
    SoftwareItem,
)
from mods.persistence import Persistence


class TestPersistence:
    """Test suite for persistence.py."""

    def test_hardware_item_persistence(self):
        """Test saving and retrieving HardwareItem instances."""
        logger = LoggingConfig().get_logger()
        logger.info("Starting test_hardware_item_persistence")

        # Initialize Persistence with a DuckDB database for testing
        duckdb_path = "test_data.db"
        if os.path.exists(duckdb_path):
            os.remove(duckdb_path)
        persistence = Persistence("duckdb:///" + duckdb_path)
        persistence.create_tables()

        # Create a HardwareItem instance
        model = HardwareItem(
            name="Production Server",
            hardware_type="server",
            is_cloud=False,
            hardware_vendor="Dell",
        )
        model.add_property("cpu", "Intel Xeon")
        model.add_property("ram", "128GB")

        # Save the model to the database
        saved_model = persistence.save(model)

        # Retrieve the model by ID
        retrieved_model = persistence.get_by_id(HardwareItem, str(saved_model.id))
        assert retrieved_model is not None
        assert retrieved_model.id == saved_model.id
        assert retrieved_model.name == "Production Server"
        assert retrieved_model.hardware_type == "server"
        assert retrieved_model.hardware_vendor == "Dell"
        assert retrieved_model.get_property("cpu") == "Intel Xeon"

        # Cleanup
        for model in persistence.get_all(HardwareItem):
            persistence.delete(model)

        assert len(persistence.get_all(HardwareItem)) == 0, (
            "Database should be empty after deletions"
        )

        logger.info("test_hardware_item_persistence completed successfully")

    def test_software_item_persistence(self):
        """Test saving and retrieving SoftwareItem instances."""
        logger = LoggingConfig().get_logger()
        logger.info("Starting test_software_item_persistence")

        # Initialize Persistence with a DuckDB database for testing
        duckdb_path = "test_data.db"
        if os.path.exists(duckdb_path):
            os.remove(duckdb_path)
        persistence = Persistence("duckdb:///" + duckdb_path)
        persistence.create_tables()

        # Create a SoftwareItem instance
        model = SoftwareItem(
            name="Web Application",
            software_type="application",
            is_cloud=True,
            is_internal=True,
            software_vendor="Internal Development",
        )
        model.add_property("version", "2.0.0")
        model.add_property("language", "Python")

        # Save the model to the database
        saved_model = persistence.save(model)

        # Retrieve the model by ID
        retrieved_model = persistence.get_by_id(SoftwareItem, str(saved_model.id))
        assert retrieved_model is not None
        assert retrieved_model.id == saved_model.id
        assert retrieved_model.name == "Web Application"
        assert retrieved_model.software_type == "application"
        assert retrieved_model.is_cloud is True
        assert retrieved_model.is_internal is True
        assert retrieved_model.get_property("version") == "2.0.0"

        # Cleanup
        for model in persistence.get_all(SoftwareItem):
            persistence.delete(model)

        assert len(persistence.get_all(SoftwareItem)) == 0, (
            "Database should be empty after deletions"
        )

        logger.info("test_software_item_persistence completed successfully")

    def test_database_item_persistence(self):
        """Test saving and retrieving DatabaseItem instances."""
        logger = LoggingConfig().get_logger()
        logger.info("Starting test_database_item_persistence")

        # Initialize Persistence with a DuckDB database for testing
        duckdb_path = "test_data.db"
        if os.path.exists(duckdb_path):
            os.remove(duckdb_path)
        persistence = Persistence("duckdb:///" + duckdb_path)
        persistence.create_tables()

        # Create a DatabaseItem instance
        model = DatabaseItem(
            name="Persistent Model",
            database_instance="prod-db-01",
            database_name="production_db",
            database_schema="public",
            database_vendor="PostgreSQL",
        )
        model.add_property("gpu", "NVIDIA RTX 3080")
        model.add_property("storage", "1TB SSD")

        # Save the model to the database
        saved_model = persistence.save(model)

        # Retrieve the model by ID
        retrieved_model = persistence.get_by_id(DatabaseItem, str(saved_model.id))
        assert retrieved_model is not None
        assert retrieved_model.id == saved_model.id
        assert retrieved_model.name == "Persistent Model"
        assert retrieved_model.get_property("gpu") == "NVIDIA RTX 3080"

        retrieved_model.add_property("ram", "32GB")
        retrieved_model.add_property("case", "laptop")
        updated_model = persistence.save(retrieved_model)
        assert updated_model.get_property("ram") == "32GB"
        assert updated_model.get_property("case") == "laptop"

        # Retrieve all models
        found_id = False
        all_models = persistence.get_all(DatabaseItem)
        for model in all_models:
            logger.info(f"Model ID: {model.id}, Name: {model.name}")
            if model.id == saved_model.id:
                found_id = True

        assert found_id, "Saved model ID should be in the list of all models"

        logger.info(f"Total models in database: {len(all_models)}")
        for model in all_models:
            persistence.delete(model)

        assert len(persistence.get_all(DatabaseItem)) == 0, (
            "Database should be empty after deletions"
        )

        logger.info("test_database_item_persistence completed successfully")

    def test_process_item_persistence(self):
        """Test saving and retrieving ProcessItem instances."""
        logger = LoggingConfig().get_logger()
        logger.info("Starting test_process_item_persistence")

        # Initialize Persistence with a DuckDB database for testing
        duckdb_path = "test_data.db"
        if os.path.exists(duckdb_path):
            os.remove(duckdb_path)
        persistence = Persistence("duckdb:///" + duckdb_path)
        persistence.create_tables()

        # Create a ProcessItem instance
        model = ProcessItem(
            name="Data Pipeline",
        )
        model.add_property("schedule", "daily")
        model.add_property("owner", "data-team")

        # Save the model to the database
        saved_model = persistence.save(model)

        # Retrieve the model by ID
        retrieved_model = persistence.get_by_id(ProcessItem, str(saved_model.id))
        assert retrieved_model is not None
        assert retrieved_model.id == saved_model.id
        assert retrieved_model.name == "Data Pipeline"
        assert retrieved_model.get_property("schedule") == "daily"

        # Cleanup
        for model in persistence.get_all(ProcessItem):
            persistence.delete(model)

        assert len(persistence.get_all(ProcessItem)) == 0, (
            "Database should be empty after deletions"
        )

        logger.info("test_process_item_persistence completed successfully")

    def test_person_item_persistence(self):
        """Test saving and retrieving PersonItem instances."""
        logger = LoggingConfig().get_logger()
        logger.info("Starting test_person_item_persistence")

        # Initialize Persistence with a DuckDB database for testing
        duckdb_path = "test_data.db"
        if os.path.exists(duckdb_path):
            os.remove(duckdb_path)
        persistence = Persistence("duckdb:///" + duckdb_path)
        persistence.create_tables()

        # Create a PersonItem instance
        model = PersonItem(
            name="John Doe",
        )
        model.add_property("email", "john.doe@example.com")
        model.add_property("department", "Engineering")

        # Save the model to the database
        saved_model = persistence.save(model)

        # Retrieve the model by ID
        retrieved_model = persistence.get_by_id(PersonItem, str(saved_model.id))
        assert retrieved_model is not None
        assert retrieved_model.id == saved_model.id
        assert retrieved_model.name == "John Doe"
        assert retrieved_model.get_property("email") == "john.doe@example.com"

        # Cleanup
        for model in persistence.get_all(PersonItem):
            persistence.delete(model)

        assert len(persistence.get_all(PersonItem)) == 0, (
            "Database should be empty after deletions"
        )

        logger.info("test_person_item_persistence completed successfully")

    def test_model_type_property_persistence(self):
        """Test saving and retrieving ModelTypeProperty instances."""
        logger = LoggingConfig().get_logger()
        logger.info("Starting test_model_type_property_persistence")

        # Initialize Persistence with a DuckDB database for testing
        duckdb_path = "test_data.db"
        if os.path.exists(duckdb_path):
            os.remove(duckdb_path)
        persistence = Persistence("duckdb:///" + duckdb_path)
        persistence.create_tables()

        # Create a ModelTypeProperty instance
        model = ModelTypeProperty(
            model_type=ModelType.SOFTWARE,
            property_key="version",
            property_value="1.0.0",
        )

        # Save the model to the database
        saved_model = persistence.save(model)

        # Retrieve the model by ID
        retrieved_model = persistence.get_by_id(ModelTypeProperty, str(saved_model.id))
        assert retrieved_model is not None
        assert retrieved_model.id == saved_model.id
        assert retrieved_model.property_key == "version"
        assert retrieved_model.property_value == "1.0.0"

        all_models = persistence.get_all(ModelTypeProperty)
        assert len(all_models) == 1, (
            "There should be exactly one ModelTypeProperty in the database"
        )
        logger.info(f"Total models in database: {len(all_models)}")
        for model in all_models:
            persistence.delete(model)

        assert len(persistence.get_all(ModelTypeProperty)) == 0, (
            "Database should be empty after deletions"
        )

        logger.info("test_model_type_property_persistence completed successfully")
