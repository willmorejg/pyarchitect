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
import json
from mods.logging_config import LoggingConfig
from mods.models import ModelType, SuperModel

logger = LoggingConfig().logger


class TestModels:
    """Test suite for models.py"""

    def test_models(self):
        """
        Test the SuperModel creation and attributes.
        """
        logger.info("Starting test_models")

        # set up test values
        name = "Test Model"
        model_type = ModelType.SOFTWARE
        properties = {"cpu": "Intel i7", "ram": "16GB", "os": "Ubuntu 22.04"}

        properties_json = json.dumps(properties)

        # Create SuperModel instance; properties needs JSON serialization
        model = SuperModel(
            name=name,
            model_type=model_type,
            properties=properties_json,
        )

        # Validate model attributes
        assert model.name == name
        assert model.model_type == model_type
        assert model.is_active is True
        assert model.revision == 1
        assert model.tags == []
        # properties is stored as dict
        assert model.properties == properties

        logger.info("Created SuperModel:", model=str(model))
        logger.info("Completed test_models successfully")
