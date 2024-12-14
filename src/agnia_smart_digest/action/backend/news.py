from newsapi import NewsApiClient
from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.utils.logger import Logger

logger = Logger("news-action")


class NewsActionInputParams(BaseModel):
    n_articles: int
    news_api_key: str


class NewsArticle(BaseModel):
    title: str
    url: str


class NewsActionOutputParams(BaseModel):
    articles: list[str]


def news_message(raw_data: dict) -> tuple[str, dict]:
    output = NewsActionOutputParams.model_validate(raw_data)

    n = len(output.articles)
    word = "article"
    if n > 1:
        word = "articles"

    formatted_message = f"<i>Fetched {n} {word} ✅</i>\n"

    for article in output.articles:
        article = NewsArticle.model_validate_json(article)
        formatted_message += f"📰 <a href='{article.url}'>{article.title}</a>\n"

    return formatted_message, output.model_dump()


@register_action(
    input_type=NewsActionInputParams,
    output_type=NewsActionOutputParams,
    system_name="General",
    result_message_func=news_message,
)
class NewsAction(Action[NewsActionInputParams, NewsActionOutputParams]):
    action_name = "news_action"

    def __init__(self):
        super().__init__(action_name="news_action")

    async def execute(
        self, input_data: NewsActionInputParams
    ) -> NewsActionOutputParams:
        client = NewsApiClient(api_key=input_data.news_api_key)

        top_headlines = client.get_top_headlines(
            language="ru",
            page_size=input_data.n_articles,
            page=1,
            country="ru",
        )

        articles = []
        for article in top_headlines["articles"]:
            articles.append(
                NewsArticle(
                    title=article["title"], url=article["url"]
                ).model_dump_json()
            )

        return NewsActionOutputParams(articles=articles)
