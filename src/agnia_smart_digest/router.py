import json

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import action_registry


async def execute_action(
    system_name: str,
    action_name: str,
    input_data: dict,
    authorizations_data: dict | None = None,
) -> dict:
    action_obj = action_registry.get_action_object(system_name, action_name)
    input_type = action_registry.get_input_type(system_name, action_name)

    # Convert input_data to a format suitable for the action
    input_params = input_type(**input_data)
    if isinstance(action_obj, type) and issubclass(action_obj, Action):
        # Instantiate and execute the action if it's a class
        action = action_obj()  # type: ignore
        output = await action.execute(input_params)
    else:
        # Execute the action directly if it's a function
        output = action_obj(authorizations_data, input_params)

    output_json = json.loads(output.json())
    return output_json


def form_result_message(
    system_name: str, action_name: str, execution_result: dict | None
) -> dict:
    if execution_result is None:
        message_str = f"Could not run action '{action_name}' for system '{system_name}'"
        message_dict = {
            "Error": f"Could not run action '{action_name}' for system '{system_name}'"
        }
        return {"message_str": message_str, "message_dict": message_dict}

    message_forming_func = action_registry.get_result_message_former(
        system_name=system_name, action_name=action_name
    )
    if message_forming_func is None:
        return {}

    result: tuple = message_forming_func(execution_result)
    return {"message_str": result[0], "message_dict": result[1]}
