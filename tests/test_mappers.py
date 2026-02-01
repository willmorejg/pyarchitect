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
from mods.models import ConfigurationItem, ModelType

logger = LoggingConfig().get_logger()


class TestMappers:
    """Test suite for mappers.py"""

    def test_model_to_dataframe_mapper(self):
        """
        Test the ModelToDataframeMapper functionality.
        """
        logger.info("Starting test_model_to_dataframe_mapper")

        # set up test model instances
        model1 = ConfigurationItem(
            name="Model One",
            model_type=ModelType.HARDWARE,
        )
        model1_properties = [{"gpu": "NVIDIA RTX 3080"}, {"storage": "1TB SSD"}]
        for prop in model1_properties:
            for key, value in prop.items():
                model1.add_property(key, value)

        model2 = ConfigurationItem(
            name="Model Two",
            model_type=ModelType.SOFTWARE,
        )

        model2_properties = [{"language": "Python"}, {"framework": "FastAPI"}]
        for prop in model2_properties:
            for key, value in prop.items():
                model2.add_property(key, value)

        mapper = ModelToDataframeMapper()
        df = mapper.marshal([model1, model2])

        # Validate dataframe contents
        assert not df.empty
        assert df.shape[0] == 2  # two rows for two models
        assert "name" in df.columns

        # Validate flattened properties columns
        assert "properties.gpu" in df.columns
        assert "properties.storage" in df.columns
        assert "properties.language" in df.columns
        assert "properties.framework" in df.columns

        # Check values are correctly mapped
        assert df.loc[0, "properties.gpu"] == "NVIDIA RTX 3080"
        assert df.loc[0, "properties.storage"] == "1TB SSD"
        assert df.loc[1, "properties.language"] == "Python"
        assert df.loc[1, "properties.framework"] == "FastAPI"

        logger.info("Created DataFrame from models:\n", df=df)
        logger.info("Completed test_model_to_dataframe_mapper successfully")
