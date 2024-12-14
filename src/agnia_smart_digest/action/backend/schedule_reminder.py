import asyncio
from datetime import datetime

from pydantic import BaseModel

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.external_services.telegram import TelegramBot
from agnia_smart_digest.utils.logger import Logger

logger = Logger("schedule-reminder-action")


class ScheduleReminderInputParams(BaseModel):
    reminder_text: str
    reminder_datetime: str
    telegram_user_id: int


class ScheduleReminderOutputParams(BaseModel):
    reminder_datetime: str


def schedule_reminder_message(data: dict) -> tuple[str, dict]:
    obj = ScheduleReminderOutputParams.model_validate(data)

    date = datetime.fromisoformat(obj.reminder_datetime)

    return (
        f"<i>Scheduled reminder ✅</i>\n📅 {date.strftime('%c')}",
        obj.model_dump(),
    )


def launch_reminder_task(data: ScheduleReminderInputParams) -> None:
    date = datetime.fromisoformat(data.reminder_datetime)

    async def reminder_task():
        try:
            logger.info(f"reminder task started at {datetime.now()}")
            logger.info(f"reminder task will be executed at {date}")

            await asyncio.sleep((datetime.now() - date).total_seconds() - 5)

            while datetime.now() < date:
                await asyncio.sleep(1)

            await TelegramBot.send_message(
                chat_id=data.telegram_user_id,
                message=data.reminder_text,
            )
        except asyncio.CancelledError:
            logger.info("reminder task cancelled")

    asyncio.create_task(reminder_task())


@register_action(
    ScheduleReminderInputParams,
    ScheduleReminderOutputParams,
    "General",
    result_message_func=schedule_reminder_message,
)
class ScheduleReminderAction(
    Action[ScheduleReminderInputParams, ScheduleReminderOutputParams]
):
    action_name = "schedule_reminder_action"

    def __init__(self) -> None:
        super().__init__("schedule_reminder_action")

    async def execute(
        self, input_data: ScheduleReminderInputParams
    ) -> ScheduleReminderOutputParams:

        launch_reminder_task(input_data)

        return ScheduleReminderOutputParams(
            reminder_datetime=input_data.reminder_datetime
        )
