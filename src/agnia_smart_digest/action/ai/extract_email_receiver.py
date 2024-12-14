from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.llm import LLM
from agnia_smart_digest.utils.helpers import prepare_prompt


class ExtractEmailReceiverActionInputParams(BaseModel):
    user_request: str


class ExtractEmailReceiverActionOutputParams(BaseModel):
    extracted_receiver: str


def extract_email_receiver_message(data: dict) -> tuple[str, dict]:
    obj = ExtractEmailReceiverActionOutputParams.model_validate(data)
    return (
        f"<i>Extracted receiver from request ✅</i>\n👤 {obj.extracted_receiver}",
        obj.model_dump(),
    )


@register_action(
    ExtractEmailReceiverActionInputParams,
    ExtractEmailReceiverActionOutputParams,
    "General",
    result_message_func=extract_email_receiver_message,
)
class ExtractEmailReceiverAction(
    Action[
        ExtractEmailReceiverActionInputParams, ExtractEmailReceiverActionOutputParams
    ]
):
    action_name = "extract_email_receiver_action"

    def __init__(self) -> None:
        super().__init__("extract_email_receiver_action")

        self.llm = LLM()
        self.stop = "</Answer>"
        self.max_tokens = 50
        self.temperature = 0.1

    async def execute(
        self, input_data: ExtractEmailReceiverActionInputParams
    ) -> ExtractEmailReceiverActionOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {"prompt": prompt, "stop": self.stop, "max_tokens": self.max_tokens}
        )
        return ExtractEmailReceiverActionOutputParams(extracted_receiver=answer)

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
Extract email address of the receiver from the user request. Do not add any other text.
Do not add any additional information.
</Instruction>


<Example>
<User review>
Please send email to a.kudryavtsev@innopolis.ru saying
"Hello, I want a daily digest message at 9 AM summarizing emails from outlook"
</User review>
<Answer>a.kudryavtsev@innopolis.ru</Answer>
</Example>

<Question>
<User review>{USER_REQUEST}</User review>
<Answer>"""
