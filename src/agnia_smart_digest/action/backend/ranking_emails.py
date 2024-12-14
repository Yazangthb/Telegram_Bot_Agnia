import json
import pickle
from collections import defaultdict
from pathlib import Path

import numpy as np
from lexrank import STOPWORDS, LexRank
from pydantic import BaseModel

from agnia_smart_digest.action.backend.emails import EmailOutputModel
from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.utils.logger import Logger

logger = Logger("ranking-emails-action")

# Load the LexRank object from a file
lex_rank_filepath = Path("models") / "tech_lexRank.pkl"
lxr = LexRank(
    documents=[["tech"]],
    stopwords=STOPWORDS["en"],
)

with lex_rank_filepath.open("rb") as f:
    data = pickle.load(f)

    score = defaultdict(lambda: 0.0)
    score.update(data)
    lxr.idf_score = score


# Define input parameters for the action
class RankingEmailsActionInputParams(BaseModel):
    emails: list[str]


# Define output parameters for the action
class RankingEmailsActionOutputParams(BaseModel):
    emails: list[str]


def remove_multiple_newlines(text: str) -> str:
    return " ".join(text.split())


def get_email_contents(json_emails: list[str]) -> list[str]:
    emails = [json.loads(email)["Text"] for email in json_emails]

    contents = []
    for email in emails:
        contents.append(remove_multiple_newlines(email))
    return contents


def return_technical_emails(contents: list[str]) -> list[int]:
    scores_cont = lxr.rank_sentences(
        contents,
        threshold=None,
        fast_power_method=False,
    )
    sorted_indices = np.argsort(scores_cont)
    return sorted_indices[::-1].tolist()


def ranking_emails_message(raw_data: dict) -> tuple[str, dict]:
    output = RankingEmailsActionOutputParams.model_validate(raw_data)

    emails = [EmailOutputModel.model_validate_json(email) for email in output.emails]

    formatted_message = "<i>Ranked technical emails ✅</i>:"
    for email in emails:
        formatted_message += f"\n📧 {email.Subject}"

    return formatted_message, output.model_dump()


# Register the action
@register_action(
    input_type=RankingEmailsActionInputParams,
    output_type=RankingEmailsActionOutputParams,
    system_name="General",
    result_message_func=ranking_emails_message,
)
class RankingEmailsAction(
    Action[RankingEmailsActionInputParams, RankingEmailsActionOutputParams]
):
    action_name = "ranking_emails_action"

    def __init__(self):
        super().__init__(action_name="ranking_emails_action")

    async def execute(
        self, input_data: RankingEmailsActionInputParams
    ) -> RankingEmailsActionOutputParams:
        contents = get_email_contents(input_data.emails)
        if not contents:
            logger.error("No email contents found")
            return RankingEmailsActionOutputParams(emails=[])

        top_emails = return_technical_emails(contents)

        selected_emails = [input_data.emails[i] for i in top_emails]

        return RankingEmailsActionOutputParams(emails=selected_emails)
