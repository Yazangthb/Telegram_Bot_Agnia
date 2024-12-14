from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.llm import LLM
from agnia_smart_digest.utils.helpers import prepare_prompt


class ExtractSearchQueryActionInputParams(BaseModel):
    user_request: str


class ExtractSearchQueryActionOutputParams(BaseModel):
    extracted_query: str


def extract_search_query_message(data: dict) -> tuple[str, dict]:
    obj = ExtractSearchQueryActionOutputParams.model_validate(data)
    return (
        f"<i>Extracted query from request ✅</i>\n🔎 {obj.extracted_query}",
        obj.model_dump(),
    )


@register_action(
    ExtractSearchQueryActionInputParams,
    ExtractSearchQueryActionOutputParams,
    "General",
    result_message_func=extract_search_query_message,
)
class ExtractSearchQueryAction(
    Action[ExtractSearchQueryActionInputParams, ExtractSearchQueryActionOutputParams]
):
    action_name = "extract_search_query_action"

    def __init__(self) -> None:
        super().__init__("extract_search_query_action")

        self.llm = LLM()
        self.stop = "</Answer>"
        self.max_tokens = 500
        self.temperature = 0.1

    async def execute(
        self, input_data: ExtractSearchQueryActionInputParams
    ) -> ExtractSearchQueryActionOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {"prompt": prompt, "stop": self.stop, "max_tokens": self.max_tokens}
        )
        return ExtractSearchQueryActionOutputParams(extracted_query=answer)

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
Extract search query from the user request. Do not add any other text.
Do not add any additional information. Remove quotes.
</Instruction>


<Example>
<User review>I want top 5 emails related to booking</User review>
<Answer>emails related to booking</Answer>
</Example>


<Question>
<User review>{USER_REQUEST}</User review>
<Answer>"""
