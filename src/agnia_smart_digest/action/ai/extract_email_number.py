from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.llm import LLM
from agnia_smart_digest.utils.helpers import prepare_prompt


class ExtractEmailNumberActionInputParams(BaseModel):
    user_request: str


class ExtractEmailNumberActionOutputParams(BaseModel):
    extracted_email_number: int


def extract_email_number_message(data: dict) -> tuple[str, dict]:
    obj = ExtractEmailNumberActionOutputParams.model_validate(data)

    return (
        f"<i>Extracted number of emails: {obj.extracted_email_number} ✅</i>",
        obj.model_dump(),
    )


@register_action(
    ExtractEmailNumberActionInputParams,
    ExtractEmailNumberActionOutputParams,
    system_name="General",
    result_message_func=extract_email_number_message,
)
class ExtractEmailNumberAction(
    Action[ExtractEmailNumberActionInputParams, ExtractEmailNumberActionOutputParams]
):
    action_name = "extract_email_number_action"

    def __init__(self):
        super().__init__("extract_email_number_action")

        self.llm = LLM()
        self.stop = "</Answer>"
        self.max_tokens = 50
        self.temperature = 0.1

    async def execute(
        self, input_data: ExtractEmailNumberActionInputParams
    ) -> ExtractEmailNumberActionOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {"prompt": prompt, "stop": self.stop, "max_tokens": self.max_tokens}
        )
        return ExtractEmailNumberActionOutputParams(extracted_email_number=int(answer))

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
Find the number of emails in the user request.
If such information is not available, return 3.
If the number is greater than 10, return 10.
If the number is less than 1, return 1.
Return only the number.
</Instruction>


<Example>
<User review>
Hello, I would like to receive 5 emails. Thank you.
</User review>
<Answer>5</Answer>
</Example>

<Example>
<User review>
Give me negative five emails! Right now!
</User review>
<Answer>1</Answer>
</Example>


<Question>
<User review>{USER_REQUEST}</User review>
<Answer>"""
