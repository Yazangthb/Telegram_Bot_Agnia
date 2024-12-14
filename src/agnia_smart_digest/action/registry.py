import json
from collections.abc import Callable
from typing import Any

import aiohttp
from pydantic import BaseModel

from agnia_smart_digest.action.exception import (
    ActionNotFoundException,
    SystemNotFoundException,
)
from agnia_smart_digest.utils.logger import Logger

logger = Logger("action-registry")


class ActionRegistry:
    def __init__(self):
        self._actions = {}

    def register_action(
        self,
        system_name: str,
        action_name: str,
        action_obj: Any,
        input_type: type[BaseModel],
        output_type: type[BaseModel],
        result_message_func: Callable | None = None,
    ):
        logger.debug(f"registering action: {action_name} for system: {system_name}")
        if system_name not in self._actions:
            logger.debug(f"creating new system: {system_name}")
            self._actions[system_name] = {}

        logger.debug(
            f"{system_name}/{action_name} is "
            f"{action_obj.__name__}({input_type.__name__}) -> {output_type.__name__}"
        )

        self._actions[system_name][action_name] = {
            "object": action_obj,
            "input_type": input_type,
            "output_type": output_type,
            "result_message_func": result_message_func,
        }

    def get_action_object(self, system_name: str, action_name: str) -> Any:
        try:
            return self._actions[system_name][action_name]["object"]
        except KeyError as e:
            if system_name not in self._actions:
                raise SystemNotFoundException(
                    f"System '{system_name}' not found"
                ) from e
            raise ActionNotFoundException(
                f"Action '{action_name}' not found for system '{system_name}'"
            ) from e

    def get_input_type(self, system_name: str, action_name: str) -> type[BaseModel]:
        try:
            return self._actions[system_name][action_name]["input_type"]
        except KeyError as e:
            if system_name not in self._actions:
                raise SystemNotFoundException(
                    f"System '{system_name}' not found"
                ) from e
            raise ActionNotFoundException(
                f"Action '{action_name}' not found for system '{system_name}'"
            ) from e

    def get_output_type(self, system_name: str, action_name: str) -> type[BaseModel]:
        try:
            return self._actions[system_name][action_name]["output_type"]
        except KeyError as e:
            if system_name not in self._actions:
                raise SystemNotFoundException(
                    f"System '{system_name}' not found"
                ) from e
            raise ActionNotFoundException(
                f"Action '{action_name}' not found for system '{system_name}'"
            ) from e

    def get_result_message_former(self, system_name: str, action_name: str) -> Callable:
        try:
            return self._actions[system_name][action_name]["result_message_func"]
        except KeyError as e:
            if system_name not in self._actions:
                raise SystemNotFoundException(
                    f"System '{system_name}' not found"
                ) from e
            raise ActionNotFoundException(
                f"Action '{action_name}' not found for system '{system_name}'"
            ) from e

    def get_parameters(self, param_cls):
        schema = param_cls.model_json_schema()
        params = schema["properties"]
        for name in params:
            params[name]["description"] = params[name].pop("title", "")
            params[name]["required"] = name in schema["required"]

            if params[name]["type"] == "array" and "$ref" in params[name]["items"]:
                params[name]["items"] = self.get_parameters(
                    param_cls.get_field_info(name)["type"]
                )
        return params

    def get_input_parameters_schema(self, system_name: str, action_name: str) -> dict:
        return self.get_parameters(self.get_input_type(system_name, action_name))

    def get_output_parameters_schema(self, system_name: str, action_name: str) -> dict:
        return self.get_parameters(self.get_output_type(system_name, action_name))

    def get_action_schema(self, system_name: str, action_name: str) -> dict:
        return {
            "system_name": system_name,
            "action_name": action_name,
            "description": self.get_action_object(system_name, action_name).__name__,
            "input_parameters": self.get_input_parameters_schema(
                system_name, action_name
            ),
            "output_parameters": self.get_output_parameters_schema(
                system_name, action_name
            ),
        }

    async def register_actions(self, url, token):
        async with aiohttp.ClientSession() as session:
            _ = session
            data = []

            for system_name, actions in self._actions.items():
                for action_name in actions:
                    data.append(self.get_action_schema(system_name, action_name))

            logger.info(f"registering actions data {json.dumps(data)}")

            async with session.post(
                url, json=data, headers={"Authorization": f"Bearer {token}"}
            ) as response:
                if response.status // 100 != 2:
                    logger.error(f"failed to register actions: {response.text}")

            logger.info("successfully registered actions")


# Create a global action registry
action_registry = ActionRegistry()


def register_action(
    input_type: type[BaseModel],
    output_type: type[BaseModel],
    system_name: str = "General",
    action_name: str | None = None,
    result_message_func: Callable | None = None,
):
    def decorator(action_obj: Any):
        nonlocal action_name
        if not action_name:
            action_name = getattr(action_obj, "action_name", None)
        if not action_name:
            if hasattr(action_obj, "__name__"):
                action_obj_name = action_obj.__name__
            else:
                action_obj_name = action_obj

            raise ValueError(
                f"Action object {action_obj_name} must have an 'action_name'"
                " attribute or 'action_name' must be provided."
            )

        action_registry.register_action(
            system_name,
            action_name,
            action_obj,
            input_type,
            output_type,
            result_message_func=result_message_func,
        )
        return action_obj

    return decorator
