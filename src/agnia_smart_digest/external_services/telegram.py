import aiohttp

from agnia_smart_digest.settings import team_auth_settings


class TelegramBot:
    @staticmethod
    async def send_message(chat_id, message):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.telegram.org/bot"
                + team_auth_settings.bot_token
                + "/sendMessage",
                data={
                    "chat_id": chat_id,
                    "text": message,
                },
            ) as response:
                response.raise_for_status()
