import heapq
import re

import nltk
from pydantic import BaseModel

from agnia_smart_digest.action.backend.emails import EmailOutputModel
from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action


def summarize_email(email_text: str) -> str:
    # Removing Square Brackets and Extra Spaces
    email_text = re.sub(r"\[[0-9]*\]", " ", email_text)
    email_text = re.sub(r"\s+", " ", email_text)
    # Removing special characters and digits
    formatted_email_text = re.sub("[^a-zA-Z]", " ", email_text)
    formatted_email_text = re.sub(r"\s+", " ", formatted_email_text)
    sentence_list = nltk.sent_tokenize(email_text)
    stopwords = nltk.corpus.stopwords.words("english")

    word_frequencies = {}
    for word in nltk.word_tokenize(formatted_email_text):
        if word not in stopwords:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1
        maximum_frequncy = max(word_frequencies.values())
    for word in word_frequencies.keys():
        word_frequencies[word] = word_frequencies[word] / maximum_frequncy
        sentence_scores = {}
    for sent in sentence_list:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(" ")) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)  # type: ignore

    summary = " ".join(summary_sentences)
    return summary


class SummarizeEmailsInputParams(BaseModel):
    emails: list[str]


class EmailSummaryOutputParams(BaseModel):
    emails: list[str]


def summarized_emails_message(raw_data: dict) -> tuple[str, dict]:
    output = EmailSummaryOutputParams.model_validate(raw_data)

    n = len(output.emails)
    word = "email"
    if n > 1:
        word = "emails"

    formatted_message = f"<i>Summarized {n} {word} ✅</i>\n"

    for email_data in output.emails:
        email_data = EmailOutputModel.model_validate_json(email_data)
        formatted_message += (
            f"✉️ «{email_data.Subject}» {email_data.Date}\n{email_data.Text}\n\n"
        )

    return formatted_message, output.model_dump()


@register_action(
    input_type=SummarizeEmailsInputParams,
    output_type=EmailSummaryOutputParams,
    system_name="General",
    result_message_func=summarized_emails_message,
)
class EmailsAction(Action[SummarizeEmailsInputParams, EmailSummaryOutputParams]):
    action_name = "summarize_emails_action"

    def __init__(self):
        super().__init__(action_name="summarize_emails_action")

    async def execute(
        self, input_data: SummarizeEmailsInputParams
    ) -> EmailSummaryOutputParams:
        emails = []
        for email in input_data.emails:
            emails.append(EmailOutputModel.model_validate_json(email))

        summarized_emails = []
        for email in emails:
            email.Text = summarize_email(email.Text)
            summarized_emails.append(email.model_dump_json())

        return EmailSummaryOutputParams(emails=summarized_emails)
