from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.llm import LLM
from agnia_smart_digest.utils.helpers import prepare_prompt


class ExtractFormatActionInputParams(BaseModel):
    user_request: str


class ExtractFormatActionOutputParams(BaseModel):
    extracted_format: str


def extract_format_message(data: dict) -> tuple[str, dict]:
    obj = ExtractFormatActionOutputParams.model_validate(data)
    return f"<i>Extracted «{obj.extracted_format}» format ✅</i>", obj.model_dump()


@register_action(
    ExtractFormatActionInputParams,
    ExtractFormatActionOutputParams,
    system_name="General",
    result_message_func=extract_format_message,
)
class ExtractFormatAction(
    Action[ExtractFormatActionInputParams, ExtractFormatActionOutputParams]
):
    action_name = "extract_format_action"

    def __init__(self):
        super().__init__("extract_format_action")

        self.llm = LLM()
        self.stop = "</Answer>"
        self.max_tokens = 50
        self.temperature = 0.1

    async def execute(
        self, input_data: ExtractFormatActionInputParams
    ) -> ExtractFormatActionOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {"prompt": prompt, "stop": self.stop, "max_tokens": self.max_tokens}
        )
        return ExtractFormatActionOutputParams(extracted_format=answer)

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
Extract the format of the message the user is requesting (peom, essay, short summary)
</Instruction>


<Example>
<User review>
Hello, I want a daily digest message at 9 AM summarizing emails from outlook
</User review>
<Answer>Short Summary</Answer>
</Example>


<Question>
<User review>{USER_REQUEST}</User review>
<Answer>"""
