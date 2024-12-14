import imaplib
from email import policy
from email.parser import BytesParser

from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.utils.logger import Logger

logger = Logger("list-emails-action")


class EmailsInputParams(BaseModel):
    outlook_email: str
    outlook_password: str
    last_n_emails: int


class EmailOutputModel(BaseModel):
    Subject: str
    From: str
    To: str
    Date: str
    Text: str


class EmailsOutputParams(BaseModel):
    emails: list[str]


def emails_message(raw_data: dict) -> tuple[str, dict]:
    output = EmailsOutputParams.model_validate(raw_data)

    n = len(output.emails)
    word = "email"
    if n > 1:
        word = "emails"

    return f"<i>Extracted {n} {word} ✅</i>", output.model_dump()


@register_action(
    input_type=EmailsInputParams,
    output_type=EmailsOutputParams,
    system_name="General",
    result_message_func=emails_message,
)
class EmailsAction(Action[EmailsInputParams, EmailsOutputParams]):
    action_name = "list_emails_action"

    def __init__(self):
        super().__init__(action_name="list_emails_action")

    async def execute(self, input_data: EmailsInputParams) -> EmailsOutputParams:
        # IMAP server settings
        IMAP_HOST = "mail.innopolis.ru"
        IMAP_PORT = 993  # IMAP over SSL/TLS
        EMAIL_ADDRESS = input_data.outlook_email
        EMAIL_PASSWORD = input_data.outlook_password

        mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)

        mail.select("INBOX")

        # Search for latest emails
        result, data = mail.uid("search", "ALL")
        email_uids = data[0].split()

        # Fetch only the last n emails
        if len(email_uids) > input_data.last_n_emails:
            email_uids = email_uids[-input_data.last_n_emails :]

        emails_data = []

        for uid in email_uids:
            # Fetch the email
            result, email_data = mail.uid("fetch", uid, "(RFC822)")
            raw_email = email_data[0][1]

            # Parse the email using BytesParser
            msg = BytesParser(policy=policy.default).parsebytes(raw_email)

            # Extract email title and text description
            email_info = EmailOutputModel(
                Subject=msg["Subject"],
                From=msg["From"],
                To=msg["To"],
                Date=msg["Date"],
                Text="",
            )

            # Find and decode the email body
            for part in msg.walk():
                content_type = part.get_content_type()

                if part.is_multipart():
                    continue
                else:
                    charset = part.get_content_charset() or "utf-8"
                    payload = part.get_payload(decode=True)

                    if isinstance(payload, bytes):
                        try:
                            decoded_payload = payload.decode(charset, errors="replace")
                            email_info.Text += decoded_payload + "\n"
                        except Exception as e:
                            logger.info(f"Error decoding part: {e}")

            # Append email info to list
            emails_data.append(email_info.model_dump_json())

        mail.logout()

        return EmailsOutputParams(
            emails=emails_data,
        )
