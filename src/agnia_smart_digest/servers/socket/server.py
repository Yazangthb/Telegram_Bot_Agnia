import asyncio
import json
from enum import StrEnum

import websockets
from pydantic import BaseModel, ValidationError

from agnia_smart_digest.router import execute_action, form_result_message
from agnia_smart_digest.settings import endpoints_settings, team_auth_settings
from agnia_smart_digest.utils.logger import Logger

logger = Logger("socket-server")


class ResultStatusEnum(StrEnum):
    SUCCESS = "Success"
    FAIL = "Fail"


class MessageModel(BaseModel):
    request_id: str
    system_name: str
    action_name: str
    input_data: dict
    system_authorization_data: dict | None


async def handle_message(input_data: dict, data: dict) -> dict:
    error_message = None
    stats = ResultStatusEnum.SUCCESS
    execution_result = None

    try:
        msg = MessageModel.model_validate(data)

        with logger.activity(f"execute-action-{msg.action_name}"):
            execution_result = await execute_action(
                msg.system_name,
                msg.action_name,
                msg.input_data,
                msg.system_authorization_data,
            )

            message = form_result_message(
                msg.system_name, msg.action_name, execution_result
            )
    except ValidationError as e:
        stats = ResultStatusEnum.FAIL
        error_message = "message validation failed"
        logger.error(f"message validation failed with error: {e.json()}")
    except Exception as e:
        stats = ResultStatusEnum.FAIL
        error_message = f"unexpected error: {e}"
        logger.error(f"unexpected error: {e}")

    response = {
        **input_data,
        **message,
        "request_id": msg.request_id,
        "status": stats.value,
    }

    if execution_result is not None:
        response["result"] = execution_result

    if error_message is not None:
        response["error_message"] = error_message

    return response


async def run():
    endpoint = f"{endpoints_settings.socket_endpoint}/{team_auth_settings.team_id}"
    async with websockets.connect(endpoint) as socket:
        logger.info("started socker server")

        try:
            while True:
                request_raw = await socket.recv()
                request = json.loads(request_raw)

                if "error" in request:
                    logger.error(f"received error message: {request}")
                    continue

                response = await handle_message(request, request)
                response_raw = json.dumps(response)

                await socket.send(response_raw)
        except websockets.ConnectionClosedOK:
            logger.info("closed by connection closing")
        except asyncio.CancelledError:
            logger.info("closed by task cancellation")
        except Exception as e:
            logger.error(f"unexpected error: {e}")
