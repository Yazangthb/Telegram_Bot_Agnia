from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TeamSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # no defaults are provided, so startup fails if settings are not specified
    team_id: str = Field(alias="TEAM_ID")
    access_token: str = Field(alias="ACCESS_TOKEN")
    bot_token: str = Field(alias="BOT_TOKEN")
    outlook_email: str = Field(alias="OUTLOOK_EMAIL")
    outlook_password: str = Field(alias="OUTLOOK_PASSWORD")

    teamflame_email: str = Field(alias="TEAMFLAME_EMAIL")
    teamflame_password: str = Field(alias="TEAMFLAME_PASSWORD")

    maps_api_key: str = Field(alias="MAPS_API_KEY")
    news_api_key: str = Field(alias="NEWS_API_KEY")

    moodle_email: str = Field(alias="MOODLE_EMAIL")
    moodle_password: str = Field(alias="MOODLE_PASSWORD")

    telegram_user_id: int = Field(alias="TELEGRAM_USER_ID")


class EnpointsSettings(BaseSettings):
    llm_endpoint: str = "http://10.100.30.244:1322/llm/get_response"
    embedder_endpoint: str = "http://10.100.30.244:1322/embedder/get_response"
    save_auth_endpoint: str = "http://10.100.30.244:9200/save-authorization-data"
    socket_endpoint: str = "ws://10.100.30.244:8200/actions-ws"
    api_endpoint: str = "http://10.100.30.244:9200"


team_auth_settings = TeamSettings()  # type: ignore
endpoints_settings = EnpointsSettings()
