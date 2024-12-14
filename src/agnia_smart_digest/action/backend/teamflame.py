import aiohttp
from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.exception import ActionException
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.utils.logger import Logger

logger = Logger("teamflame-action")


class TeamFlameInputParams(BaseModel):
    teamflame_email: str
    teamflame_password: str


class TaskOutputModel(BaseModel):
    name: str
    description: str


class TeamFlameOutputParams(BaseModel):
    teamflame_tasks: list[str]


def tasks_message(raw_data: dict) -> tuple[str, dict]:
    output = TeamFlameOutputParams.model_validate(raw_data)

    n = len(output.teamflame_tasks)
    word = "task"
    if n > 1:
        word = "tasks"

    formatted_message = f"<i>Extracted {n} {word} ✅</i>\n"

    for task_data in output.teamflame_tasks:
        task_data = TaskOutputModel.model_validate_json(task_data)
        formatted_message += (
            f"📝 «{task_data.name}»"
            + (f": {task_data.description}" if task_data.description else "")
            + "\n"
        )

    return formatted_message, output.model_dump()


@register_action(
    input_type=TeamFlameInputParams,
    output_type=TeamFlameOutputParams,
    system_name="General",
    result_message_func=tasks_message,
)
class TeamflameAcrion(Action[TeamFlameInputParams, TeamFlameOutputParams]):
    action_name = "list_teamflake_tasks_action"

    def __init__(self):
        super().__init__(action_name="list_teamflake_tasks_action")

    async def execute(self, input_data: TeamFlameInputParams) -> TeamFlameOutputParams:
        AUTH_BASE_URL = "https://auth-api.teamflame.ru"
        DATA_BASE_URL = "https://api.teamflame.ru"

        EMAIL_ADDRESS = input_data.teamflame_email
        PASSWORD = input_data.teamflame_password

        #### LOGIN
        url = f"{AUTH_BASE_URL}/auth/sign-in"
        body = {"email": EMAIL_ADDRESS, "password": PASSWORD}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=body) as response:
                if response.status == 200:
                    tokens = (await response.json())["tokens"]
                else:
                    raise ActionException("Error loggin in to teamflame!")

        #### Fetch data
        tasks_info = []

        url = f"{DATA_BASE_URL}/tasks/my"
        headers = {
            "Authorization": f"Bearer {tokens['accessToken']['token']}",
            "X-Api-Version": "1",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    tasks_info = await response.json()
                else:
                    raise ActionException("Failed to get tasks")
        ####

        tasks_data = []
        for task in tasks_info:
            task_info = TaskOutputModel(
                name=task["name"], description=task["description"]
            )
            tasks_data.append(task_info.model_dump_json())

        return TeamFlameOutputParams(teamflame_tasks=tasks_data)
