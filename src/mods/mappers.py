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

import pandas as pd

from .logging_config import LoggingConfig

logger = LoggingConfig().get_logger()

class ModelToDataframeMapper:
    """
    A class responsible for mapping model instances to dataframes.
    """

    def marshal(self, model_instances: list[object]) -> pd.DataFrame:
        """
        Marshals a model instance to a dictionary representing a dataframe row.
        :param model_instances: The model instances to be mapped.
        :return: A dataframe representing the model instance.
        """
        model_dicts = [m.model_dump() for m in model_instances]
        logger.info("Marshalled model instances to dicts", model_dicts=model_dicts)
        model_json = json.dumps(model_dicts, default=str)
        logger.info("Converted model dicts to JSON", model_json=model_json)
        return pd.DataFrame()# pd.json_normalize(model_json)
