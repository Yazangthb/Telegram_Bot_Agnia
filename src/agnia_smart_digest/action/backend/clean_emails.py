import re

from pydantic import BaseModel

from agnia_smart_digest.action.backend.emails import EmailOutputModel
from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action


class CleanEmailsInputParams(BaseModel):
    emails: list[str]


class CleanEmailsOutputParams(BaseModel):
    emails: list[str]


def clean_emails_message(data: dict) -> tuple[str, dict]:
    output = CleanEmailsOutputParams.model_validate(data)

    n = len(output.emails)
    word = "email"
    if n > 1:
        word = "emails"

    return f"<i>Preprocessed {n} {word} ✅</i>", output.model_dump()


@register_action(
    input_type=CleanEmailsInputParams,
    output_type=CleanEmailsOutputParams,
    system_name="General",
    result_message_func=clean_emails_message,
)
class EmailsAction(Action[CleanEmailsInputParams, CleanEmailsOutputParams]):
    action_name = "clean_emails_action"

    def __init__(self):
        super().__init__(action_name="clean_emails_action")

    async def execute(
        self, input_data: CleanEmailsInputParams
    ) -> CleanEmailsOutputParams:
        emails = []
        for email in input_data.emails:
            emails.append(EmailOutputModel.model_validate_json(email))

        cleaned_emails = []
        for email in emails:
            email.Text = self.clean_email(email.Text)
            cleaned_emails.append(email.model_dump_json())

        return CleanEmailsOutputParams(emails=cleaned_emails)

    def clean_email(self, email: str) -> str:
        return re.sub(r"\<.*?\>", "", email)
