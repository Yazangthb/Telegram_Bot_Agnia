import aiohttp

from agnia_smart_digest.settings import endpoints_settings, team_auth_settings


class LLM:
    def __init__(self):
        self.url: str = endpoints_settings.llm_endpoint

    async def get_response(self, json_data) -> str:
        async with aiohttp.ClientSession() as session:
            json_data["team_id"] = team_auth_settings.team_id
            async with session.post(self.url, json=json_data) as response:
                if response.status != 200:
                    raise Exception(f"Error: {response.status}")
                return await response.json()
