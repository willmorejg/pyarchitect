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
from mods.models import ConfigurationItem, ModelType

logger = LoggingConfig().logger


class TestModels:
    """Test suite for models.py"""

    def test_models(self):
        """
        Test the ConfigurationItem creation and attributes.
        """
        logger.info("Starting test_models")

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

        logger.info("Created SuperModel:", model=str(model))
        logger.info("Completed test_models successfully")
