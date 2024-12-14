import chromadb
from pydantic import BaseModel

from agnia_smart_digest.action.backend.emails import EmailOutputModel
from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.utils.logger import Logger

client = chromadb.Client()

collection = client.create_collection("emails31")


logger = Logger("search-emails-action")


# Define input parameters for the action
class SearchEmailsActionInputParams(BaseModel):
    emails: list[str]
    query_texts: str
    n_results: int


# Define output parameters for the action
class SearchEmailActionOutputParams(BaseModel):
    emails: list[str]


def search_emails_message(raw_data: dict) -> tuple[str, dict]:
    output = SearchEmailActionOutputParams.model_validate(raw_data)

    n = len(output.emails)
    word = "email"
    if n > 1:
        word = "emails"

    formatted_message = f"Find {n} {word} ✅"
    return formatted_message, output.model_dump()


# Register the action
@register_action(
    input_type=SearchEmailsActionInputParams,
    output_type=SearchEmailActionOutputParams,
    system_name="General",
    result_message_func=search_emails_message,
)
class SearchEmailsAction(
    Action[SearchEmailsActionInputParams, SearchEmailActionOutputParams]
):
    action_name = "search_emails_action"

    def __init__(self):
        super().__init__(action_name="search_emails_action")

    async def execute(
        self, input_data: SearchEmailsActionInputParams
    ) -> SearchEmailActionOutputParams:
        try:
            emails = [
                EmailOutputModel.model_validate_json(email)
                for email in input_data.emails
            ]
            documents = [email.Text for email in emails]
            metadatas = [{"topic": email.Subject} for email in emails]

            ids = list(map(str, range(len(documents))))

            # Add documents to the collection
            collection.add(
                documents=documents,
                metadatas=metadatas,  # type: ignore
                ids=ids,
            )

            # Query the collection
            results = collection.query(
                query_texts=[input_data.query_texts], n_results=input_data.n_results
            )
            assert results["ids"] is not None

            indexes = [int(index) for index in results["ids"][0]]

            return SearchEmailActionOutputParams(
                emails=[input_data.emails[index] for index in indexes]
            )
        except Exception as e:
            logger.error(f"Error in collection action: {e}")
            return SearchEmailActionOutputParams(emails=[])
