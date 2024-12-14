import asyncio
from pathlib import Path

import psutil
from bs4 import BeautifulSoup
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from agnia_smart_digest.action.base import Action
from agnia_smart_digest.action.registry import register_action
from agnia_smart_digest.utils.logger import Logger

driver_path = Path() / "driver"
msedgedriver_path = list(driver_path.glob("msedgedriver"))[0].resolve()

# Configure Selenium WebDriver for Edge
edge_options = Options()
edge_options.add_argument("--headless")  # Run in headless mode
edge_options.add_argument("--no-sandbox")
edge_options.add_argument("--disable-dev-shm-usage")


logger = Logger("moodle-action")


class MoodleInputParams(BaseModel):
    moodle_email: str
    moodle_password: str


class MoodleOutputModel(BaseModel):
    name: str
    date: str
    time: str
    course_info: str
    # event_url: str


class MoodleOutputParams(BaseModel):
    deadlines: list[str]


def deadlines_message(raw_data: dict) -> tuple[str, dict]:
    output = MoodleOutputParams.model_validate(raw_data)

    word = "deadline"
    if len(output.deadlines) > 1:
        word = "deadlines"

    formatted_message = (
        f"<i>Fetched {len(output.deadlines)} {word} from Moodle ✅</i>\n"
    )

    for deadline in output.deadlines:
        deadline = MoodleOutputModel.model_validate_json(deadline)
        formatted_message += (
            f"🎯 {deadline.course_info.removeprefix('Assignment is due · ')}:\n"
            f"• «{deadline.name}» is due <b>{deadline.time} on {deadline.date}</b>\n\n"
        )

    return formatted_message, output.model_dump()


@register_action(
    input_type=MoodleInputParams,
    output_type=MoodleOutputParams,
    system_name="General",
    result_message_func=deadlines_message,
)
class EmailsAction(Action[MoodleInputParams, MoodleOutputParams]):
    action_name = "moodle_action"

    def __init__(self):
        super().__init__(action_name="moodle_action")

    async def execute(self, input_data: MoodleInputParams) -> MoodleOutputParams:

        service = EdgeService(executable_path=str(msedgedriver_path))

        driver = webdriver.Edge(service=service, options=edge_options)

        deadlines = []

        try:
            # Step 1: Log out previous user
            logger.info("logging-out from moodle")
            logout_url = "https://sso.university.innopolis.ru/adfs/oauth2/logout"
            driver.get(logout_url)
            await asyncio.sleep(1)  # Allow time for the logout to complete

            # Step 2: Log into the secondary website
            logger.info("logging-in to moodle")
            login_url = "https://my.university.innopolis.ru/site/auth?authclient=adfs"
            driver.get(login_url)
            await asyncio.sleep(3)  # Allow time for the page to load

            # Find and fill the login form
            logger.info("filling-in moodle login form")
            driver.find_element(By.ID, "userNameInput").send_keys(
                input_data.moodle_email
            )
            driver.find_element(By.ID, "passwordInput").send_keys(
                input_data.moodle_password
            )
            driver.find_element(By.ID, "submitButton").click()
            await asyncio.sleep(3)  # Allow time for the login process to complete

            # Step 3: Navigate to Moodle and use OAuth login
            logger.info("navigating to moodle")
            moodle_login_url = "https://moodle.innopolis.university/login/index.php"
            driver.get(moodle_login_url)
            await asyncio.sleep(1)  # Allow time for the page to load

            # Wait for the OAuth login button to be clickable
            logger.info("waiting for moodle login button")
            oauth_login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, ".login-identityproviders a.btn")
                )
            )
            oauth_login_button.click()

            logger.info("navigating to moodle dashboard")

            dashboard_url = "https://moodle.innopolis.university/my/"
            driver.get(dashboard_url)

            # log_page_source(driver, "Opened Dashboard")

            # Wait for the timeline section to be visible using the data-block attribute
            logger.info("waiting for moodle timeline section")
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, 'section[data-block="timeline"]')
                )
            )

            # Give the page a moment to fully render
            logger.info("waiting for moodle page to load")
            await asyncio.sleep(1)

            # Get the page source after fully loaded
            page_source = driver.page_source

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(page_source, "html.parser")

            # Example: Find and logger.info the timeline header
            logger.info("finding timeline header")
            timeline_header = soup.find("section", {"data-block": "timeline"}).find(
                "h3"
            )
            if not timeline_header:
                logger.info("Timeline header not found.")

            # Example: Find and logger.info the list of tasks
            logger.info("finding timeline tasks")
            tasks = soup.find("section", {"data-block": "timeline"})

            # Find all date sections
            date_sections = soup.find_all(
                "div", {"data-region": "event-list-content-date"}
            )

            # Iterate over each date section and extract events
            logger.info("iterating over timeline events")
            for date_section in date_sections:
                # Get the date text
                date_text = date_section.find("h5").text.strip()

                # Get the sibling list group containing the events
                list_group = date_section.find_next_sibling(
                    "div", {"class": "list-group list-group-flush"}
                )

                # Find all events within the list group
                events = list_group.find_all("div", {"data-region": "event-list-item"})

                for event in events:
                    # Extract event details
                    time = event.find(
                        "small",
                        {"class": "text-right text-nowrap align-self-center ml-1"},
                    ).text.strip()
                    event_name = (
                        event.find("h6", {"class": "event-name"}).find("a").text.strip()
                    )
                    event_url = event.find("h6", {"class": "event-name"}).find("a")[
                        "href"
                    ]
                    course_info = event.find("small", {"class": "mb-0"}).text.strip()

                    # Store the event details in a dictionary
                    event_details = {
                        "date": date_text,
                        "time": time,
                        "event_name": event_name,
                        "event_url": event_url,
                        "course_info": course_info,
                    }

                    # Append the event details to the deadlines list
                    deadlines.append(event_details)
        finally:
            # Close the driver
            driver.quit()

            # Ensure that all Edge processes are terminated
            for proc in psutil.process_iter(["pid", "name"]):
                if (
                    proc.info["name"] == "msedgedriver.exe"
                    or proc.info["name"] == "msedge.exe"
                ):
                    proc.kill()

        logger.info("moodle deadlines fetched")
        deadlines_data = []
        for deadline in deadlines:
            deadline_info = MoodleOutputModel(
                name=deadline["event_name"],
                date=deadline["date"],
                time=deadline["time"],
                course_info=deadline["course_info"],
                # event_url=deadline["event_url"]
            )
            deadlines_data.append(deadline_info.model_dump_json())
        return MoodleOutputParams(deadlines=deadlines_data)
