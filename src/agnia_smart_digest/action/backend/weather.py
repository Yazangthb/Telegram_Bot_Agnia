import python_weather
import python_weather.forecast
from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.exception import ActionException
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.utils.logger import Logger

logger = Logger("weather-action")


class WeatherInputParams(BaseModel):
    city: str


class WeatherOutputParams(BaseModel):
    morning_temperature: int
    morning_icon: str

    afternoon_temperature: int
    afternoon_icon: str

    evening_temperature: int
    evening_icon: str


def weather_message(raw_data: dict) -> tuple[str, dict]:
    output = WeatherOutputParams.model_validate(raw_data)

    formatted_message = (
        "<i>Fetched today's weather ✅</i>\n"
        f"🌆 Morning - {output.morning_icon} {output.morning_temperature}°C\n"
        f"🏙️ Afternoon - {output.afternoon_icon} {output.afternoon_temperature}°C\n"
        f"🌃 Evening - {output.evening_icon} {output.evening_temperature}°C"
    )

    return formatted_message, output.model_dump()


@register_action(
    input_type=WeatherInputParams,
    output_type=WeatherOutputParams,
    system_name="General",
    result_message_func=weather_message,
)
class WeatherAction(Action[WeatherInputParams, WeatherOutputParams]):
    SUN = "☀️"
    RAIN = "🌧️"
    SNOW = "❄️"
    CLOUD = "☁️"

    action_name = "weather_action"

    def __init__(self):
        super().__init__(action_name="weather_action")

    async def execute(self, input_data: WeatherInputParams) -> WeatherOutputParams:
        async with python_weather.Client(
            unit=python_weather.METRIC,  # type: ignore
            locale=python_weather.enums.Locale.RUSSIAN,
        ) as client:
            weather = await client.get(input_data.city)
            logger.debug(
                f"received weather for {weather.location} at {weather.datetime}"
            )

            today_forecast = None
            for forecast in weather.daily_forecasts:
                today_forecast = forecast
                break

            if today_forecast is None:
                raise ActionException("Failed to get today's forecast")

            morning_forecast = None
            afternoon_forecast = None
            evening_forecast = None
            for forecast in today_forecast.hourly_forecasts:
                if forecast.time.hour == 9:
                    morning_forecast = forecast
                    continue
                elif forecast.time.hour == 12:
                    afternoon_forecast = forecast
                    continue
                elif forecast.time.hour == 18:
                    evening_forecast = forecast
                    continue

            if (
                morning_forecast is None
                or afternoon_forecast is None
                or evening_forecast is None
            ):
                raise ActionException(
                    "Failed to get morning, afternoon, and evening forecasts"
                )

        return WeatherOutputParams(
            morning_temperature=morning_forecast.temperature,
            morning_icon=self.select_weather_icon(morning_forecast),
            afternoon_temperature=afternoon_forecast.temperature,
            afternoon_icon=self.select_weather_icon(afternoon_forecast),
            evening_temperature=evening_forecast.temperature,
            evening_icon=self.select_weather_icon(evening_forecast),
        )

    def select_weather_icon(
        self, forecast: python_weather.forecast.HourlyForecast
    ) -> str:
        if forecast.chances_of_rain > 40:
            return self.RAIN
        elif forecast.chances_of_snow > 40:
            return self.SNOW
        elif forecast.cloud_cover > 40:
            return self.CLOUD
        else:
            return self.SUN
