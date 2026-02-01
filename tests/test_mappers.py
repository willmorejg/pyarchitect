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
from mods.mappers import ModelToDataframeMapper
from mods.models import ModelType, SuperModel

logger = LoggingConfig().get_logger()

class TestMappers:
    """Test suite for mappers.py"""

    def test_model_to_dataframe_mapper(self):
        """
        Test the ModelToDataframeMapper functionality.
        """
        logger.info("Starting test_model_to_dataframe_mapper")

        # set up test model instances
        model1 = SuperModel(
            name="Model One",
            model_type=ModelType.HARDWARE,
            properties=[("gpu", "NVIDIA RTX 3080"), ("storage", "1TB SSD")],
        )
        model2 = SuperModel(
            name="Model Two",
            model_type=ModelType.SOFTWARE,
            properties=[("language", "Python"), ("framework", "FastAPI")],
        )

        mapper = ModelToDataframeMapper()
        df = mapper.marshal([model1, model2])

        # Validate dataframe contents
        assert not df.empty
        assert df.shape[0] == 2  # two rows for two models
        assert "name" in df.columns

        logger.info("Created DataFrame from models:\n", df=df)
        logger.info(" properties:\n", properties=df.properties)
        logger.info("Completed test_model_to_dataframe_mapper successfully")
