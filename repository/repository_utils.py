import json
from copy import deepcopy
from typing import Tuple

from pynamodb.attributes import MapAttribute
from pynamodb.models import Model

from constants.common_constants import CommonConstants


class RepositoryUtils:
    @staticmethod
    def get_update(old_data: dict, new_data: dict) -> Tuple[bool, dict]:
        """
        Updates the contents of a dictionary based on new data provided.

        :param old_data: Original dictionary.
        :type old_data: dict

        :param new_data: New data to add to old dictionary.
        :type new_data: dict

        :return: A boolean that tells whether there are changes, and the updated data.
        :rtype: Tuple[bool, dict]
        """

        excluded_comparison_keys = deepcopy(CommonConstants.EXCLUDE_COMPARISON_KEYS)

        # copy old_data
        old_data_copy = deepcopy(old_data)
        for key in excluded_comparison_keys:
            old_data_copy.pop(key, None)

        # set updated_data
        updated_data = deepcopy(old_data_copy)
        RepositoryUtils.update_nested_dict(updated_data, new_data)
        has_update = updated_data != old_data_copy

        # Change to MapAttribute
        updated_data = RepositoryUtils.items_to_map_attr(updated_data)

        return has_update, updated_data

    @staticmethod
    def update_nested_dict(old_dict: dict, new_data: dict) -> dict:
        """
        Updates the contents of a nested dictionary.

        :param old_dict: Dictionary to add updates.
        :type old_dict: dict

        :param new_data: New data to add to old dictionary.
        :type new_data: dict
        
        :return: Old dictionary with updated values from new data.
        :rtype: dict
        """

        for key, val in new_data.items():
            if isinstance(val, dict):
                try:
                    RepositoryUtils.update_nested_dict(old_dict[key], val)
                except KeyError:
                    old_dict[key] = {}
                    RepositoryUtils.update_nested_dict(old_dict[key], val)
            elif val is not None or key in old_dict:
                old_dict[key] = val

        return old_dict

    @staticmethod
    def items_to_map_attr(hub_dict: dict) -> dict:
        """
        Convert nested dicts to MapAttribute.

        :param hub_dict: Dict to update.
        :type hub_dict: dict

        :return: Dict with MapAttribute.
        :rtype: dict
        """

        tmp_dict = {}
        for key, val in hub_dict.items():
            if isinstance(val, dict):
                new_dict = RepositoryUtils.items_to_map_attr(val)
                tmp_dict[key] = MapAttribute(**new_dict)
            else:
                tmp_dict[key] = val
        return tmp_dict

    @staticmethod
    def db_model_to_dict(model: Model) -> dict:
        """
        Converts pynamodb Model to dict.

        :param model: Pynamo Model to convert.
        :type model: Model
        
        :return: Converted Pynamo Model.
        :rtype: dict
        """

        json_str = model.to_json()
        hub_dict = json.loads(json_str)
        return hub_dict

    @staticmethod
    def load_data(pydantic_schema_in, exclude_unset=False):
        """
        Converts a pydantic schema to dict.

        :param pydantic_schema_in: A pydantic schema.
        :type pydantic_schema_in: PydanticSchemaIn

        :param exclude_unset: Whether to exclude unset., defaults to False
        :type exclude_unset: bool, optional
        
        :return: A dictionary representing the pydantic schema.
        :rtype: dict
        """

        return json.loads(pydantic_schema_in.json(exclude_unset=exclude_unset))
