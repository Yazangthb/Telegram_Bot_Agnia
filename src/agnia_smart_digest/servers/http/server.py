from __future__ import annotations

import json
from contextlib import asynccontextmanager

import aiohttp
import requests
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

from agnia_smart_digest.action.registry import action_registry
from agnia_smart_digest.servers.http.exception import (
    InvalidCredentialsError,
    ServerAuthorizationError,
    UserAuthorizationError,
)
from agnia_smart_digest.servers.http.gitflame import authorize_in_git_flame
from agnia_smart_digest.servers.http.utils import save_authorization_data
from agnia_smart_digest.settings import endpoints_settings, team_auth_settings
from agnia_smart_digest.utils.helpers import strip_url
from agnia_smart_digest.utils.logger import Logger

logger = Logger("http-server")


router = APIRouter()


class GitFlameCredentials(BaseModel):
    username: str
    password: str


@router.post("/authorize/git-flame")
async def authorize_in_git_flame_and_send(credentials: GitFlameCredentials):
    try:
        authorization_data = authorize_in_git_flame(
            credentials.username, credentials.password
        )

    except requests.ConnectionError as e:
        raise HTTPException(
            status_code=503, detail="GitFlame is currently unavailable"
        ) from e
    except requests.exceptions.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, detail="Error in decoding response from GitFlame"
        ) from e
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error occurred when sending request to GitFlame",
        ) from e
    except ServerAuthorizationError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except (InvalidCredentialsError, UserAuthorizationError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return save_authorization_data(authorization_data, "GitFlame")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("starting server")

    url = "/".join([strip_url(endpoints_settings.api_endpoint), "register-actions"])
    with logger.activity("registering-actions"):
        await action_registry.register_actions(url, team_auth_settings.access_token)

    headers = {"Authorization": f"Bearer {team_auth_settings.access_token}"}

    # initial user credentials
    async with aiohttp.ClientSession(headers=headers) as session:
        with logger.activity("saving-user-credentials"):
            response = await session.post(
                endpoints_settings.save_auth_endpoint,
                json={
                    "system_name": "General",
                    "authorization_data_json": json.dumps({}),
                },
            )
            response.raise_for_status()

        with logger.activity("registering-new-plans"):
            plans = []
            url = "/".join([strip_url(endpoints_settings.api_endpoint), "plans"])

            # plans.append(
            #     await create_new_plan(
            #         url,
            #         session,
            #         {
            #             "initial_data": {"user_request": ""},
            #             "description": "extract platforms plan",
            #             "actions": [
            #                 {
            #                     "action_id": 1,
            #                     "system": "General",
            #                     "action_type": "TeamAction",
            #                     "action_name": "extract_platforms_action",
            #                     "input_data": {
            #                         "user_request": "initial_data[user_request]"
            #                     },
            #                     "depends_on": [],
            #                     "requires_visualization": True,
            #                 }
            #             ],
            #         },
            #     )
            # )

            # plans.append(
            #     await create_new_plan(
            #         url,
            #         session,
            #         {
            #             "initial_data": {"user_request": ""},
            #             "description": "extract format plan",
            #             "actions": [
            #                 {
            #                     "action_id": 1,
            #                     "system": "General",
            #                     "action_type": "TeamAction",
            #                     "action_name": "extract_format_action",
            #                     "input_data": {
            #                         "user_request": "initial_data[user_request]"
            #                     },
            #                     "depends_on": [],
            #                     "requires_visualization": True,
            #                 }
            #             ],
            #         },
            #     )
            # )

            plans.append(
                await create_new_plan(
                    url,
                    session,
                    {
                        "initial_data": {"city": "Innopolis"},
                        "description": (
                            "weather, sunny, temperature,"
                            " humidity, rain, cloud, wear, clother"
                        ),
                        "actions": [
                            {
                                "action_id": 1,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "weather_action",
                                "input_data": {"city": "initial_data[city]"},
                                "depends_on": [],
                                "requires_visualization": True,
                            }
                        ],
                    },
                )
            )

            plans.append(
                await create_new_plan(
                    url,
                    session,
                    {
                        "initial_data": {
                            "user_request": "",
                            "outlook_email": team_auth_settings.outlook_email,
                            "outlook_password": team_auth_settings.outlook_password,
                        },
                        "description": "get, emails, list, fetch, inbox, contacts",
                        "actions": [
                            {
                                "action_id": 1,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "extract_email_number_action",
                                "input_data": {
                                    "user_request": "initial_data[user_request]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 2,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "list_emails_action",
                                "input_data": {
                                    "outlook_email": "initial_data[outlook_email]",
                                    "outlook_password": "initial_data[outlook_password]",
                                    "last_n_emails": "actions[1][extracted_email_number]",
                                },
                                "depends_on": [1],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 3,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "clean_emails_action",
                                "input_data": {
                                    "emails": "actions[2][emails]",
                                },
                                "depends_on": [2],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 4,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "ranking_emails_action",
                                "input_data": {
                                    "emails": "actions[3][emails]",
                                },
                                "depends_on": [3],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 5,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "summarize_emails_action",
                                "input_data": {
                                    "emails": "actions[4][emails]",
                                },
                                "depends_on": [4],
                                "requires_visualization": True,
                            },
                        ],
                    },
                )
            )

            plans.append(
                await create_new_plan(
                    url,
                    session,
                    {
                        "initial_data": {
                            "teamflame_email": team_auth_settings.teamflame_email,
                            "teamflame_password": team_auth_settings.teamflame_password,
                        },
                        "description": (
                            "tasks, cards, board, kanban, teamflame, todo, work"
                        ),
                        "actions": [
                            {
                                "action_id": 1,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "list_teamflake_tasks_action",
                                "input_data": {
                                    "teamflame_email": "initial_data[teamflame_email]",
                                    "teamflame_password": "initial_data[teamflame_password]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            }
                        ],
                    },
                )
            )

            plans.append(
                await create_new_plan(
                    url,
                    session,
                    {
                        "initial_data": {
                            "travel_source": "Stuttgart",
                            "travel_destination": "Karlsruhe",
                            "api_key": team_auth_settings.maps_api_key,
                        },
                        "description": (
                            "route, travel, distance, "
                            "time, latency, map, gps, arrive"
                        ),
                        "actions": [
                            {
                                "action_id": 1,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "travel_time_action",
                                "input_data": {
                                    "travel_source": "initial_data[travel_source]",
                                    "travel_destination": "initial_data[travel_destination]",
                                    "api_key": "initial_data[api_key]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            }
                        ],
                    },
                )
            )

            plans.append(
                await create_new_plan(
                    url,
                    session,
                    {
                        "initial_data": {
                            "news_api_key": team_auth_settings.news_api_key,
                            "user_request": "",
                        },
                        "description": (
                            "news, articles, newspaper, "
                            "headline, world, happning, info"
                        ),
                        "actions": [
                            {
                                "action_id": 1,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "extract_acticle_number_action",
                                "input_data": {
                                    "user_request": "initial_data[user_request]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 2,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "news_action",
                                "input_data": {
                                    "news_api_key": "initial_data[news_api_key]",
                                    "n_articles": "actions[1][extracted_article_number]",
                                },
                                "depends_on": [1],
                                "requires_visualization": True,
                            },
                        ],
                    },
                )
            )

            plans.append(
                await create_new_plan(
                    url,
                    session,
                    {
                        "initial_data": {
                            "moodle_email": team_auth_settings.moodle_email,
                            "moodle_password": team_auth_settings.moodle_password,
                        },
                        "description": (
                            "moodle, deadline, assignment,"
                            " task, due, submission, course, homework"
                        ),
                        "actions": [
                            {
                                "action_id": 1,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "moodle_action",
                                "input_data": {
                                    "moodle_email": "initial_data[moodle_email]",
                                    "moodle_password": "initial_data[moodle_password]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            },
                        ],
                    },
                )
            )

            plans.append(
                await create_new_plan(
                    url,
                    session,
                    {
                        "initial_data": {
                            "user_request": "",
                            "outlook_email": team_auth_settings.outlook_email,
                            "outlook_password": team_auth_settings.outlook_password,
                        },
                        "description": "send, email, sent, contact, message, text, @",
                        "actions": [
                            {
                                "action_id": 1,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "extract_email_receiver_action",
                                "input_data": {
                                    "user_request": "initial_data[user_request]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 2,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "extract_email_text_action",
                                "input_data": {
                                    "user_request": "initial_data[user_request]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 3,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "extract_email_subject_action",
                                "input_data": {
                                    "user_request": "initial_data[user_request]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 4,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "send_email_action",
                                "input_data": {
                                    "outlook_email": "initial_data[outlook_email]",
                                    "outlook_password": "initial_data[outlook_password]",
                                    "email_receiver": "actions[1][extracted_receiver]",
                                    "email_subject": "actions[3][extracted_subject]",
                                    "email_content": "actions[2][extracted_text]",
                                },
                                "depends_on": [1, 2, 3],
                                "requires_visualization": True,
                            },
                        ],
                    },
                )
            )

            plans.append(
                await create_new_plan(
                    url,
                    session,
                    {
                        "initial_data": {
                            "user_request": "",
                            "reminder_datetime": "0001-01-01T00:00:00",
                            "telegram_user_id": team_auth_settings.telegram_user_id,
                        },
                        "description": (
                            "remind, reminder, schedule, note, "
                            "postpone, calendar, event, deadline, time, date"
                        ),
                        "actions": [
                            {
                                "action_id": 1,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "extract_reminder_datetime_action",
                                "input_data": {
                                    "user_request": "initial_data[user_request]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 2,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "generate_reminder_text_action",
                                "input_data": {
                                    "user_request": "initial_data[user_request]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 3,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "schedule_reminder_action",
                                "input_data": {
                                    "reminder_text": "actions[2][reminder_text]",
                                    "reminder_datetime": "actions[1][reminder_datetime]",
                                    "telegram_user_id": "initial_data[telegram_user_id]",
                                },
                                "depends_on": [1, 2],
                                "requires_visualization": True,
                            },
                        ],
                    },
                )
            )

            plans.append(
                await create_new_plan(
                    url,
                    session,
                    {
                        "initial_data": {
                            "user_request": "",
                            "outlook_email": team_auth_settings.outlook_email,
                            "outlook_password": team_auth_settings.outlook_password,
                            "n_results": 5,
                        },
                        "description": (
                            "search, find, email, retrieve, get, "
                            "extract, topic, related to, about"
                        ),
                        "actions": [
                            {
                                "action_id": 1,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "extract_search_query_action",
                                "input_data": {
                                    "user_request": "initial_data[user_request]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 2,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "extract_email_number_action",
                                "input_data": {
                                    "user_request": "initial_data[user_request]",
                                },
                                "depends_on": [],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 3,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "list_emails_action",
                                "input_data": {
                                    "last_n_emails": "actions[2][extracted_email_number]",
                                    "outlook_email": "initial_data[outlook_email]",
                                    "outlook_password": "initial_data[outlook_password]",
                                },
                                "depends_on": [2],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 4,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "search_emails_action",
                                "input_data": {
                                    "emails": "actions[3][emails]",
                                    "query_texts": "actions[1][extracted_query]",
                                    "n_results": "initial_data[n_results]",
                                },
                                "depends_on": [1, 2, 3],
                                "requires_visualization": True,
                            },
                            {
                                "action_id": 5,
                                "system": "General",
                                "action_type": "TeamAction",
                                "action_name": "summarize_emails_action",
                                "input_data": {
                                    "emails": "actions[4][emails]",
                                },
                                "depends_on": [4],
                                "requires_visualization": True,
                            },
                        ],
                    },
                )
            )

    yield

    async with aiohttp.ClientSession(headers=headers) as session:
        for plan_id in plans:
            with logger.activity(f"deleting-plan-{plan_id}"):
                url = "/".join(
                    [strip_url(endpoints_settings.api_endpoint), "plans", plan_id]
                )
                response = await session.delete(url)

    logger.info("stopping server")


async def create_new_plan(url, session, plan):
    logger.info(f"creating plan: {json.dumps(plan)}")
    response = await session.post(url, json=plan)
    response.raise_for_status()
    return (await response.json())["plan_id"]


def build_app() -> FastAPI:
    app = FastAPI(
        debug=False,
        routes=router.routes,
        title="Agnia Smart Digest",
        summary="Agnia Smart Digest",
        description="Agnia Smart Digest",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.include_router(router)

    return app
