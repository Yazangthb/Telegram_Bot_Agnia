from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.llm import LLM
from agnia_smart_digest.utils.helpers import prepare_prompt


class ExtractEmailSubjectActionInputParams(BaseModel):
    user_request: str


class ExtractEmailSubjectActionOutputParams(BaseModel):
    extracted_subject: str


def extract_email_subject_message(data: dict) -> tuple[str, dict]:
    obj = ExtractEmailSubjectActionOutputParams.model_validate(data)
    return (
        f"<i>Extracted subject from request ✅</i>\n📬 <b>{obj.extracted_subject}</b>",
        obj.model_dump(),
    )


@register_action(
    ExtractEmailSubjectActionInputParams,
    ExtractEmailSubjectActionOutputParams,
    "General",
    result_message_func=extract_email_subject_message,
)
class ExtractEmailSubjectAction(
    Action[ExtractEmailSubjectActionInputParams, ExtractEmailSubjectActionOutputParams]
):
    action_name = "extract_email_subject_action"

    def __init__(self) -> None:
        super().__init__("extract_email_subject_action")

        self.llm = LLM()
        self.stop = "</Answer>"
        self.max_tokens = 500
        self.temperature = 0.5

    async def execute(
        self, input_data: ExtractEmailSubjectActionInputParams
    ) -> ExtractEmailSubjectActionOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {"prompt": prompt, "stop": self.stop, "max_tokens": self.max_tokens}
        )
        return ExtractEmailSubjectActionOutputParams(extracted_subject=answer)

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
Generate email subject from the user request. Do not add any other text.
It shoule be one short sentence. Do not put any punctuation.
</Instruction>


<Example>
<User review>
Please send email to a.kudryavtsev@innopolis.ru saying
"Hello, I want a daily digest message at 9 AM summarizing emails from outlook"
</User review>
<Answer>Daily Digest Request</Answer>
</Example>

<Example>
<User review>
Lorem Ipsum is simply dummy text of the printing and typesetting industry.
Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, 
when an unknown printer took a galley of type and scrambled it
to make a type specimen book. It has survived not only five centuries, but
also the leap into electronic typesetting, remaining essentially unchanged.
</User review>
<Answer>Lorem Ipsum</Answer>
</Example>


<Question>
<User review>{USER_REQUEST}</User review>
<Answer>"""
