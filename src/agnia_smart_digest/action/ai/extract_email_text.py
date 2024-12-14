from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.llm import LLM
from agnia_smart_digest.utils.helpers import prepare_prompt


class ExtractEmailTextActionInputParams(BaseModel):
    user_request: str


class ExtractEmailTextActionOutputParams(BaseModel):
    extracted_text: str


def extract_email_text_message(data: dict) -> tuple[str, dict]:
    obj = ExtractEmailTextActionOutputParams.model_validate(data)
    return (
        (
            "<i>Extracted text from request ✅</i>\n"
            f"<blockquote expandable>{obj.extracted_text}</blockquote>"
        ),
        obj.model_dump(),
    )


@register_action(
    ExtractEmailTextActionInputParams,
    ExtractEmailTextActionOutputParams,
    "General",
    result_message_func=extract_email_text_message,
)
class ExtractEmailTextAction(
    Action[ExtractEmailTextActionInputParams, ExtractEmailTextActionOutputParams]
):
    action_name = "extract_email_text_action"

    def __init__(self) -> None:
        super().__init__("extract_email_text_action")

        self.llm = LLM()
        self.stop = "</Answer>"
        self.max_tokens = 2000
        self.temperature = 0.1

    async def execute(
        self, input_data: ExtractEmailTextActionInputParams
    ) -> ExtractEmailTextActionOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {"prompt": prompt, "stop": self.stop, "max_tokens": self.max_tokens}
        )
        return ExtractEmailTextActionOutputParams(extracted_text=answer)

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
Extract email text from the user request. Do not add any other text.
Do not add any additional information. Remove quotes.
</Instruction>


<Example>
<User review>
Please send email to a.kudryavtsev@innopolis.ru saying
"Hello, I want a daily digest message at 9 AM summarizing emails from outlook"
</User review>
<Answer>Hello, I want a daily digest message at 9 AM summarizing emails from outlook</Answer>
</Example>

<Example>
<User review>
send email to a.kudryavtsev@innopolis.university saying "Hello,

I hope this email finds you well. I would like to schedule a meeting with you to discuss the upcoming project. Please let me know a convenient time for you.

Thank you.

Best regards,
Anton"
</User review>
<Answer>
Hello,

I hope this email finds you well. I would like to schedule a meeting with you to discuss the upcoming project. Please let me know a convenient time for you.

Thank you.

Best regards,
Anton
</Answer>
</Example>


<Question>
<User review>{USER_REQUEST}</User review>
<Answer>"""
