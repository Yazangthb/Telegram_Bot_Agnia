import json

from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.llm import LLM
from agnia_smart_digest.utils.helpers import prepare_prompt


class ExtractPlatformsActionInputParams(BaseModel):
    user_request: str


class ExtractPlatformsActionOutputParams(BaseModel):
    extracted_platforms: list[str]


def extract_platforms_message(data: dict) -> tuple[str, dict]:
    obj = ExtractPlatformsActionOutputParams.model_validate(data)
    return (
        "<i>Extracted «" + json.dumps(obj.extracted_platforms) + "» platforms ✅</i>",
        obj.model_dump(),
    )


@register_action(
    ExtractPlatformsActionInputParams,
    ExtractPlatformsActionOutputParams,
    system_name="General",
    result_message_func=extract_platforms_message,
)
class ExtractPlatformsAction(
    Action[ExtractPlatformsActionInputParams, ExtractPlatformsActionOutputParams]
):
    action_name = "extract_platforms_action"

    def __init__(self):
        super().__init__("extract_platforms_action")

        self.llm = LLM()
        self.stop = "</Answer>"
        self.max_tokens = 50
        self.temperature = 0.1

    async def execute(
        self, input_data: ExtractPlatformsActionInputParams
    ) -> ExtractPlatformsActionOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {"prompt": prompt, "stop": self.stop, "max_tokens": self.max_tokens}
        )
        return ExtractPlatformsActionOutputParams(
            extracted_platforms=json.loads(answer)
        )

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
Extract the platforms the user mentioned in his message
(Google Meet, gitflame, Outlook, etc..) and return them as a json list
</Instruction>


<Example>
<User review>
Hello, I want a daily digest message at 9 AM summarizing emails from outlook
</User review>
<Answer>["outlook"]</Answer>
</Example>

<Example>
<User review>
Hello, I want to get reminders about by teamflame tasks.
</User review>
<Answer>["teamflame"]</Answer>
</Example>

<Example>
<User review>
Hello, I want digest message at 9 AM twice a month summarizing emails from Gmail
</User review>
<Answer>["gmail"]</Answer>
</Example>

<Question>
<User review>{USER_REQUEST}</User review>
<Answer>"""
