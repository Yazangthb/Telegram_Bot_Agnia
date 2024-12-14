from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.llm import LLM
from agnia_smart_digest.utils.helpers import prepare_prompt


class GenerateReminderTextActionInputParams(BaseModel):
    user_request: str


class GenerateReminderTextActionOutputParams(BaseModel):
    reminder_text: str


def generate_reminder_text_message(data: dict) -> tuple[str, dict]:
    obj = GenerateReminderTextActionOutputParams.model_validate(data)
    return (
        (
            "<i>Generated reminder text ✅</i>\n"
            f"<blockquote>{obj.reminder_text}</blockquote>"
        ),
        obj.model_dump(),
    )


@register_action(
    GenerateReminderTextActionInputParams,
    GenerateReminderTextActionOutputParams,
    "General",
    result_message_func=generate_reminder_text_message,
)
class GenerateReminderTextAction(
    Action[
        GenerateReminderTextActionInputParams, GenerateReminderTextActionOutputParams
    ]
):
    action_name = "generate_reminder_text_action"

    def __init__(self) -> None:
        super().__init__("generate_reminder_text_action")

        self.llm = LLM()
        self.stop = "</Answer>"
        self.max_tokens = 500
        self.temperature = 0.7

    async def execute(
        self, input_data: GenerateReminderTextActionInputParams
    ) -> GenerateReminderTextActionOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {"prompt": prompt, "stop": self.stop, "max_tokens": self.max_tokens}
        )

        return GenerateReminderTextActionOutputParams(reminder_text=answer)

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
Generate reminder text from the user request.
Make it short and concise and add one relevant advice.
</Instruction>


<Example>
<User review>
Please remind me about presentation at 10 AM
</User review>
<Answer>You have preseantion at 10 AM, do not forget to repeat your speech</Answer>
</Example>

<Example>
<User review>
Remind me about apples in 5 minute
</User review>
<Answer>Reminder: "apples". An apple a day keeps the doctor away!</Answer>
</Example>

<Question>
<User review>{USER_REQUEST}</User review>
<Answer>"""
