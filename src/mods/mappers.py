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
from typing import Any

import pandas as pd

from .logging_config import LoggingConfig

logger = LoggingConfig().get_logger()


def _flatten_dict(
    d: dict[str, Any], parent_key: str = "", sep: str = "."
) -> dict[str, Any]:
    """
    Recursively flattens a nested dictionary.
    :param d: The dictionary to flatten.
    :param parent_key: The base key string for nested keys.
    :param sep: The separator between nested keys.
    :return: A flattened dictionary.
    """
    items: list[tuple[str, Any]] = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep).items())
        elif (
            isinstance(v, list)
            and v
            and isinstance(v[0], dict)
            and "key" in v[0]
            and "value" in v[0]
        ):
            # Handle list of key-value property dicts
            for item in v:
                prop_key = f"{new_key}{sep}{item['key']}"
                items.append((prop_key, item["value"]))
        elif isinstance(v, list):
            items.append((new_key, v))
        else:
            items.append((new_key, v))
    return dict(items)


class ModelToDataframeMapper:
    """
    A class responsible for mapping model instances to dataframes.
    """

    def marshal(self, model_instances: list[object]) -> pd.DataFrame:
        """
        Marshals model instances to a dataframe with flattened JSON structure.
        Nested dicts become dot-notation columns (e.g., 'properties.cpu').
        :param model_instances: The model instances to be mapped.
        :return: A dataframe representing the model instances with flattened columns.
        """
        model_dicts = [m.model_dump() for m in model_instances]
        logger.info("Marshalled model instances to dicts", model_dicts=model_dicts)
        flattened_dicts = [_flatten_dict(d) for d in model_dicts]
        logger.info("Flattened model dicts", flattened_dicts=flattened_dicts)
        return pd.DataFrame(flattened_dicts)
