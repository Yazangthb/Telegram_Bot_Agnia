from datetime import datetime

import humanfriendly
from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.llm import LLM
from agnia_smart_digest.utils.helpers import prepare_prompt


class ExtractReminderDatetimeActionInputParams(BaseModel):
    user_request: str


class ExtractReminderDatetimeActionOutputParams(BaseModel):
    reminder_datetime: str


def extract_reminder_datetime_message(data: dict) -> tuple[str, dict]:
    obj = ExtractReminderDatetimeActionOutputParams.model_validate(data)

    delta = datetime.fromisoformat(obj.reminder_datetime) - datetime.now()

    return (
        (
            f"<i>Extracted reminder timedelta ✅</i>\n"
            f"⏰ Will remind in {humanfriendly.format_timespan(delta.total_seconds())}"
        ),
        obj.model_dump(),
    )


@register_action(
    ExtractReminderDatetimeActionInputParams,
    ExtractReminderDatetimeActionOutputParams,
    "General",
    result_message_func=extract_reminder_datetime_message,
)
class ExtractReminderDatetimeAction(
    Action[
        ExtractReminderDatetimeActionInputParams,
        ExtractReminderDatetimeActionOutputParams,
    ]
):
    action_name = "extract_reminder_datetime_action"

    def __init__(self) -> None:
        super().__init__("extract_reminder_datetime_action")

        self.llm = LLM()
        self.stop = "</Answer>"
        self.max_tokens = 50
        self.temperature = 0.1

    async def execute(
        self, input_data: ExtractReminderDatetimeActionInputParams
    ) -> ExtractReminderDatetimeActionOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        user_request = (
            f"Current date and time is {datetime.now().isoformat()}. {user_request}"
        )
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {"prompt": prompt, "stop": self.stop, "max_tokens": self.max_tokens}
        )
        return ExtractReminderDatetimeActionOutputParams(reminder_datetime=answer)

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
You will be provided with current date and time and user request.
Your task is to generate new datetime when reminder should be executed.
</Instruction>


<Example>
<User review>
Current date and time is 2023-01-05T08:00:00. Please remind me about presentation at 10 AM
</User review>
<Answer>2023-01-05T10:00:00</Answer>
</Example>

<Example>
<User review>
Current date and time is 2024-07-07T01:1:55. Please remind me about shopping tommorow at 10 AM
</User review>
<Answer>2024-07-08T10:00:00</Answer>
</Example>

<Example>
<User review>
Current date and time is 2024-07-07T01:1:55. Remind me about apples in 5 minute
</User review>
<Answer>2024-07-07T01:06:55</Answer>
</Example>

<Question>
<User review>{USER_REQUEST}</User review>
<Answer>"""
