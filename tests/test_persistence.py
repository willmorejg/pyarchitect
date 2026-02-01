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
from mods.models import ConfigurationItem, ModelType
from mods.persistence import Persistence


class TestPersistence:
    """Test suite for persistence.py"""

    def test_persistence(self):
        """
        Test the Persistence class for saving and retrieving SuperModel instances.
        """
        logger = LoggingConfig().get_logger()
        logger.info("Starting test_persistence")

        # Initialize Persistence with a DuckDB database for testing
        duckdb_path = "test_data.db"
        if os.path.exists(duckdb_path):
            os.remove(duckdb_path)
        persistence = Persistence("duckdb:///" + duckdb_path)
        persistence.create_tables()

        # Create a SuperModel instance
        model = ConfigurationItem(
            name="Persistent Model",
            model_type=ModelType.HARDWARE,
        )
        model.add_property("gpu", "NVIDIA RTX 3080")
        model.add_property("storage", "1TB SSD")

        # Save the model to the database
        saved_model = persistence.save(model)

        # Retrieve the model by ID
        retrieved_model = persistence.get_by_id(str(saved_model.id))
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
        all_models = persistence.get_all()
        for model in all_models:
            logger.info(f"Model ID: {model.id}, Name: {model.name}")
            if model.id == saved_model.id:
                found_id = True

        assert found_id, "Saved model ID should be in the list of all models"

        logger.info(f"Total models in database: {len(all_models)}")
        for model in all_models:
            persistence.delete(model)

        assert len(persistence.get_all()) == 0, "Database should be empty after deletions"

        logger.info("test_persistence completed successfully")
