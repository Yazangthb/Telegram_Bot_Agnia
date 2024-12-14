from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.llm import LLM
from agnia_smart_digest.utils.helpers import prepare_prompt


class ExtractArticleNumberActionInputParams(BaseModel):
    user_request: str


class ExtractArticleNumberActionOutputParams(BaseModel):
    extracted_article_number: int


def extract_article_number_message(data: dict) -> tuple[str, dict]:
    obj = ExtractArticleNumberActionOutputParams.model_validate(data)

    return (
        f"<i>Extracted number of acrticles: {obj.extracted_article_number} ✅</i>",
        obj.model_dump(),
    )


@register_action(
    ExtractArticleNumberActionInputParams,
    ExtractArticleNumberActionOutputParams,
    system_name="General",
    result_message_func=extract_article_number_message,
)
class ExtractArticleNumberAction(
    Action[
        ExtractArticleNumberActionInputParams, ExtractArticleNumberActionOutputParams
    ]
):
    action_name = "extract_acticle_number_action"

    def __init__(self):
        super().__init__("extract_acticle_number_action")

        self.llm = LLM()
        self.stop = "</Answer>"
        self.max_tokens = 50
        self.temperature = 0.1

    async def execute(
        self, input_data: ExtractArticleNumberActionInputParams
    ) -> ExtractArticleNumberActionOutputParams:
        user_request = input_data.user_request
        prompt = self.get_prompt()
        prompt = prepare_prompt(prompt, user_request)
        answer = await self.llm.get_response(
            {"prompt": prompt, "stop": self.stop, "max_tokens": self.max_tokens}
        )
        return ExtractArticleNumberActionOutputParams(
            extracted_article_number=int(answer)
        )

    def get_prompt(self) -> str:
        return """<Prompt>
<Instruction>
Find the number of arcticles in the user request.
If such information is not available, return 3.
If the number is greater than 5, return 5.
If the number is less than 1, return 1.
Return only the number.
</Instruction>


<Example>
<User review>
Hello, I would like to receive 5 arcticles. Thank you.
</User review>
<Answer>5</Answer>
</Example>

<Example>
<User review>
Give me negative five arcitcles! Right now!
</User review>
<Answer>1</Answer>
</Example>


<Question>
<User review>{USER_REQUEST}</User review>
<Answer>"""
