import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from .config import (
    BOOKING_DATE_OFFSET,
    BOOKING_PREFERENCES,
    MESSAGES,
    BookingPreferences,
    Day,
)
from .pages import SportRickLoginPage
from .utils import BookingOutcomeReporter, logger

load_dotenv()

IS_DEV_ENV = os.environ["ENV"] == "dev"


class Bot:
    def __init__(self):
        self._driver = self._initialize_driver()

        self._logger = logger

        self._booking_outcome_reporter = BookingOutcomeReporter()

    def start(self, booking_preferences: BookingPreferences):
        self._logger.info(MESSAGES.action_begin)

        try:
            if self._should_book_today(list(booking_preferences)):
                self._logger.info(MESSAGES.should_book_today)
                self._book(booking_preferences)
            else:
                self._logger.info(MESSAGES.skip_today)
        except Exception as e:
            self._logger.info(MESSAGES.error.format(error=e))

            self._booking_outcome_reporter.report_failure(
                e, self._driver.get_screenshot_as_png()
            )
        finally:
            self._stop()

    def _stop(self):
        self._logger.info(MESSAGES.action_end)

        if not IS_DEV_ENV:
            self._driver.quit()

    def _book(self, booking_preferences: BookingPreferences):
        sport_rick_login_page = SportRickLoginPage(self._driver)
        polimi_login_page = sport_rick_login_page.accept_cookies().login()
        verify_otp_page = polimi_login_page.login()
        dashboard_page = verify_otp_page.verify()
        bookings_page = dashboard_page.accept_cookies().go_to_bookings()
        new_booking_page = bookings_page.new_booking()
        giurati_fit_center_booking_page = new_booking_page.select_giurati_fit_center()
        confirm_time_slot_page = giurati_fit_center_booking_page.book_time_slot(
            booking_preferences
        )

        dashboard_page = (
            confirm_time_slot_page.confirm().say_no_to_booking_another_slot()
        )

        self._booking_outcome_reporter.report_success(dashboard_page.take_screenshot())

    def _should_book_today(self, days_to_book_this_week: list[Day]) -> bool:
        """The gym allows bookings for 2 days in advance. For example, on Saturday (5)
        we want to book for Monday (0), on Sunday (6) we want to book for Tuesday (1) and so on."""
        days_to_book_adjusted_for_offset = [
            (x.value - BOOKING_DATE_OFFSET) % 7 for x in days_to_book_this_week
        ]

        today = Day.today().value
        if today not in days_to_book_adjusted_for_offset:
            return False

        return True

    def _initialize_driver(self) -> WebDriver:
        driver: WebDriver = webdriver.Chrome(
            service=None
            if IS_DEV_ENV
            else ChromeService(ChromeDriverManager().install()),
            options=self._get_chrome_driver_options(),
        )
        driver.set_window_size(1280, 720)
        driver.implicitly_wait(10)
        return driver

    def _get_chrome_driver_options(self) -> Options:
        options: Options = webdriver.ChromeOptions()

        if IS_DEV_ENV:
            # So the browser doesn't close after the script finishes. Will still close if driver.quit() is called.
            options.add_experimental_option("detach", True)
        else:
            # To run in VPS environments without a GUI
            options.add_argument("--headless")

        return options


def main():
    bot = Bot()
    bot.start(BOOKING_PREFERENCES)


if __name__ == "__main__":
    main()
