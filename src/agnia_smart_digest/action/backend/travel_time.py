import json
from datetime import datetime

import aiohttp
from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.utils.logger import Logger

logger = Logger("travel-time-action")


async def get_coordinates(place, api_key):
    url = "https://api.traveltimeapp.com/v4/geocoding/search"
    headers = {
        "Accept": "application/json",
        "X-Application-Id": "4c4b22a1",
        "X-Api-Key": api_key,
    }
    params = {
        "query": place,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            data = await response.json()
            if "features" in data and len(data["features"]) > 0:
                place_info = data["features"][0]
                address = place_info["properties"]["label"]
                longitude, latitude = place_info["geometry"]["coordinates"]
                return address, longitude, latitude
            else:
                raise ValueError(f"Could not get coordinates for {place}")


async def get_corridinates_of_start_dest(src, dst, api_key):
    src_address, src_longitude, src_latitude = await get_coordinates(src, api_key)
    dst_address, dst_longitude, dst_latitude = await get_coordinates(dst, api_key)

    logger.debug(f"source address: {src_address} ({src_longitude}, {src_latitude})")
    logger.debug(
        f"destination address: {dst_address} ({dst_longitude}, {dst_latitude})"
    )
    return [
        [src_latitude, src_longitude],
        [dst_latitude, dst_longitude],
    ]


async def get_travel_time(api_key, start_coords, end_coords, departure_time):
    # Define the endpoint and headers
    url = "https://api.traveltimeapp.com/v4/time-filter"
    headers = {
        "Content-Type": "application/json",
        "X-Application-Id": "4c4b22a1",
        "X-Api-Key": api_key,
    }

    # Define the payload data
    payload = {
        "locations": [
            {
                "id": "start-location",
                "coords": {"lat": start_coords[0], "lng": start_coords[1]},
            },
            {
                "id": "final-location",
                "coords": {"lat": end_coords[0], "lng": end_coords[1]},
            },
        ],
        "departure_searches": [
            {
                "id": "One-to-one Matrix",
                "departure_location_id": "start-location",
                "arrival_location_ids": ["final-location"],
                "departure_time": departure_time.isoformat(),
                "travel_time": 4 * 60 * 60,  # 4 hours
                "properties": ["travel_time", "distance"],
                "transportation": {"type": "driving"},
            }
        ],
    }

    # Convert payload to JSON
    payload_json = json.dumps(payload)

    # Send POST request
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload_json, headers=headers) as response:
            data = await response.json()
            return data


class TravelTimeActionInputParams(BaseModel):
    travel_source: str
    travel_destination: str
    api_key: str


class TravelTimeActionOutputParams(BaseModel):
    travel_time: int
    distance: int


def travel_time_message(raw_data: dict) -> tuple[str, dict]:
    output = TravelTimeActionOutputParams.model_validate(raw_data)

    formatted_message = "<i>Calculated time ✅</i>\n"

    word = "minute"
    if output.travel_time > 1:
        word = "minutes"

    formatted_message += f"⏰ Travel time: {output.travel_time} {word}\n"
    formatted_message += f"🗺️ Distance: {output.distance} km\n"

    return formatted_message, output.model_dump()


@register_action(
    input_type=TravelTimeActionInputParams,
    output_type=TravelTimeActionOutputParams,
    system_name="General",
    result_message_func=travel_time_message,
)
class TravelTimeAction(
    Action[TravelTimeActionInputParams, TravelTimeActionOutputParams]
):
    action_name = "travel_time_action"

    def __init__(self):
        super().__init__(action_name="travel_time_action")

    async def execute(
        self, input_data: TravelTimeActionInputParams
    ) -> TravelTimeActionOutputParams:
        source, destination = await get_corridinates_of_start_dest(
            input_data.travel_source,
            input_data.travel_destination,
            input_data.api_key,
        )

        data = await get_travel_time(
            input_data.api_key, source, destination, datetime.now()
        )

        logger.debug(f"travel time {data=}")
        travel_time = (
            data["results"][0]["locations"][0]["properties"][0]["travel_time"] // 60
        )
        distance = (
            data["results"][0]["locations"][0]["properties"][0]["distance"] // 1000
        )

        return TravelTimeActionOutputParams(travel_time=travel_time, distance=distance)
