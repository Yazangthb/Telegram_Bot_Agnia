import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.utils.logger import Logger

logger = Logger("send-email-action")


class EmailSendInputParams(BaseModel):
    outlook_email: str
    outlook_password: str
    email_receiver: str
    email_subject: str
    email_content: str


class EmailSendOutputParams(BaseModel):
    status: str


def email_send_message(raw_data: dict) -> tuple[str, dict]:
    output = EmailSendOutputParams.model_validate(raw_data)
    if output.status == "Success":
        formatted_message = "<i>Email sent successfully! ✅</i>"
    else:
        formatted_message = "<i>Email sending failed! ❌</i>"

    return formatted_message, output.model_dump()


@register_action(
    input_type=EmailSendInputParams,
    output_type=EmailSendOutputParams,
    system_name="General",
    result_message_func=email_send_message,
)
class SendEmailAction(Action[EmailSendInputParams, EmailSendOutputParams]):
    action_name = "send_email_action"

    def __init__(self):
        super().__init__(action_name="send_email_action")

    async def execute(self, input_data: EmailSendInputParams) -> EmailSendOutputParams:
        SMTP_HOST = "mail.innopolis.ru"  # Replace with your SMTP server
        SMTP_PORT = 587  # SMTP port for TLS

        try:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
            server.starttls()
            server.login(input_data.outlook_email, input_data.outlook_password)

            msg = MIMEMultipart()
            msg["From"] = input_data.outlook_email
            msg["To"] = input_data.email_receiver
            msg["Subject"] = input_data.email_subject
            msg.attach(MIMEText(input_data.email_content, "plain"))

            server.sendmail(
                input_data.outlook_email, input_data.email_receiver, msg.as_string()
            )
            server.quit()

            return EmailSendOutputParams(status="Success")
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return EmailSendOutputParams(status="Failed")
