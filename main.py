import datetime as dt
import logging
import os
import smtplib
import time
from email.message import EmailMessage
from random import gauss, randint
from typing import Callable, ParamSpec, Self, TypeVar

import pyotp
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager

from config import (
    BOOKING_PREFERENCES,
    MESSAGES,
    BookingPreferences,
    Day,
)

load_dotenv()

IS_DEV_ENV = os.environ.get("ENV") == "dev"
SMTP_EMAIL_ADDRESS = os.environ.get("SMTP_EMAIL_ADDRESS")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
DESTINATION_EMAIL_ADDRESS = os.environ.get("DESTINATION_EMAIL_ADDRESS")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

# The gym allows bookings for 2 days in advance, so we need to use this offset to select the correct date for booking.
BOOKING_DATE_OFFSET = 2

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("booking_automation.log"),
    ],
)


P = ParamSpec("P")
R = TypeVar("R")


def log_call(fn: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args, **kwds):
        logger.info(MESSAGES["action_start"].format(function_name=fn.__name__))
        return fn(*args, **kwds)

    return wrapper


class EmailSMTPClient:
    def __init__(self):
        self._smtp_server = smtplib.SMTP("smtp.gmail.com", 587)

    @log_call
    def send_email(self, msg):
        self._authenticate()
        self._smtp_server.send_message(msg)
        self._terminate_session()

    def _authenticate(self):
        self._smtp_server.starttls()
        self._smtp_server.login(SMTP_EMAIL_ADDRESS, SMTP_PASSWORD)

    def _terminate_session(self):
        self._smtp_server.quit()


class BookingOutcomeReporter:
    def __init__(self):
        self._smtp_client = EmailSMTPClient()

    @log_call
    def report_success(self, screenshot: bytes):
        msg = EmailMessage()
        msg = self._set_addressing_info(msg)
        msg["Subject"] = MESSAGES["email_success_subject"].format(
            date=self._format_booking_date()
        )
        msg.set_content(MESSAGES["email_success_body"])
        msg = self._attach_screenshot(msg, screenshot)
        self._send_email(msg)

    @log_call
    def report_failure(self, error: Exception, screenshot: bytes = None):
        msg = EmailMessage()
        msg = self._set_addressing_info(msg)
        msg["Subject"] = MESSAGES["email_failure_subject"].format(
            date=self._format_booking_date()
        )
        msg.set_content(str(error))
        if screenshot is not None:
            self._attach_screenshot(msg, screenshot)
        self._send_email(msg)

    def _send_email(self, msg: EmailMessage):
        self._smtp_client.send_email(msg)

    def _format_booking_date(self):
        booking_date = (
            dt.datetime.now() + dt.timedelta(days=BOOKING_DATE_OFFSET)
        ).strftime("%A %B %d")
        return booking_date

    def _attach_screenshot(self, msg: EmailMessage, screenshot: bytes) -> EmailMessage:
        msg.add_attachment(screenshot, maintype="image", subtype="png")
        return msg

    def _set_addressing_info(
        self,
        msg: EmailMessage,
        email_from: str = "me",
        email_to: str = DESTINATION_EMAIL_ADDRESS,
    ) -> EmailMessage:
        msg["From"] = email_from
        msg["To"] = email_to
        return msg


class Page:
    def __init__(self, driver: WebDriver):
        self._driver = driver
        self._sleep_for_a_bit()

    def take_screenshot(self):
        return self._driver.get_screenshot_as_png()

    def _sleep_for_a_bit(self, duration: int = None):
        if duration is None:
            duration = randint(1, 4)
        time.sleep(duration)

    def _fill_form_input_like_a_human(self, element: WebElement, text: str):
        mean_delay = 0.12
        std_dev = 0.04
        min_delay = 0.05

        for character in text:
            delay = max(min_delay, gauss(mean_delay, std_dev))
            element.send_keys(character)
            time.sleep(delay)


class ConfirmTimeSlotPage(Page):
    @log_call
    def confirm(self) -> Self:
        confirm_booking_button = self._driver.find_element(
            By.ID, "btnConfirmAppointmentBooking"
        )
        confirm_booking_button.click()
        return self

    @log_call
    def say_no_to_booking_another_slot(self) -> "DashboardPage":
        self._sleep_for_a_bit()
        no_button = self._driver.find_element(
            By.CSS_SELECTOR, '#srModal_g_confirm_dialog [data-modalrole="cancel"]'
        )
        no_button.click()
        return DashboardPage(self._driver)


class GiuratiFitCenterBookingPage(Page):
    # TODO: Make more robust, try booking a different slot if the prefered one is not available, etc.
    @log_call
    def book_time_slot(
        self, booking_preferences: BookingPreferences
    ) -> ConfirmTimeSlotPage:
        self._sleep_for_a_bit()
        time_slot_index = self._get_time_slot_index(booking_preferences)
        # data-date-offset 2 because we want to book for two days in advance
        time_slot = self._driver.find_element(
            By.CSS_SELECTOR,
            f'#day-schedule-container [data-date-offset="{BOOKING_DATE_OFFSET}"] div.event-slot:nth-child({time_slot_index})',
        )
        time_slot.click()
        return ConfirmTimeSlotPage(self._driver)

    def _get_time_slot_index(self, booking_preferences: BookingPreferences) -> int:
        """Get the time slot index for the day after tomorrow, because that's when we want to book for."""
        return booking_preferences.get(Day.day_after_tomorrow()).value["index"]


class NewBookingPage(Page):
    @log_call
    def select_giurati_fit_center(self) -> GiuratiFitCenterBookingPage:
        fit_center_booking_button = self._driver.find_element(
            By.CSS_SELECTOR, ".list-group-item:last-child"
        )
        fit_center_booking_button.click()
        return GiuratiFitCenterBookingPage(self._driver)


class BookingsPage(Page):
    @log_call
    def new_booking(self) -> NewBookingPage:
        new_booking_button = self._driver.find_element(
            By.CSS_SELECTOR, ".purple-plum.btn_nuovaprenotazione.standard-booking.btn"
        )
        new_booking_button.click()
        return NewBookingPage(self._driver)


class DashboardPage(Page):
    @log_call
    def accept_cookies(self) -> Self:
        """Need this because the accept cookies button sits on top of some of the time slots and could raise an ElementClickInterceptedException."""
        accept_cookies_button = self._driver.find_element(
            By.CSS_SELECTOR, ".iubenda-cs-accept-btn.iubenda-cs-btn-primary"
        )
        accept_cookies_button.click()
        return self

    @log_call
    def go_to_bookings(self) -> BookingsPage:
        bookings_page_button = self._driver.find_element(
            By.CSS_SELECTOR, "#home_btt_booking > div"
        )
        bookings_page_button.click()
        return BookingsPage(self._driver)

    @log_call
    def take_screenshot(self):
        self._is_loaded()
        return super().take_screenshot()

    def _is_loaded(self):
        return (
            self._driver.find_element(
                By.CSS_SELECTOR, "#event-repository > .event-main-block.row"
            )
            is not None
        )


class VerifyOTPPage(Page):
    @log_call
    def verify(self) -> DashboardPage:
        self._input_otp()
        self._click_verify_otp()
        return DashboardPage(self._driver)

    def _input_otp(self):
        otp_input = self._driver.find_element(By.ID, "otp")
        self._fill_form_input_like_a_human(otp_input, self._generate_otp())

    def _click_verify_otp(self):
        continue_button = self._driver.find_element(By.ID, "submit-dissms")
        continue_button.click()

    def _generate_otp(self) -> str:
        return pyotp.TOTP(os.environ["TOKEN"]).now()


class PolimiLoginPage(Page):
    @log_call
    def login(self) -> VerifyOTPPage:
        self._input_username()
        self._input_password()
        self._sleep_for_a_bit()
        self._click_login()
        return VerifyOTPPage(self._driver)

    def _input_username(self):
        username_input = self._driver.find_element(By.ID, "login")
        self._fill_form_input_like_a_human(username_input, USERNAME)

    def _input_password(self):
        password_input = self._driver.find_element(By.ID, "password")
        self._fill_form_input_like_a_human(password_input, PASSWORD)

    def _click_login(self):
        login_button_container = self._driver.find_element(
            By.CLASS_NAME, "aunicalogin-button-accedi"
        )
        login_button = login_button_container.find_element(By.TAG_NAME, "button")
        login_button.click()


class SportRickLoginPage(Page):
    _page_address = "https://ecomm.sportrick.com/sportpolimi"

    def __init__(self, driver):
        super().__init__(driver)
        self._driver.get(self._page_address)

    @log_call
    def accept_cookies(self) -> Self:
        """Need this because the accept cookies button sits on top of some of the time slots and could raise an ElementClickInterceptedException."""
        accept_cookies_button = self._driver.find_element(
            By.CSS_SELECTOR, ".iubenda-cs-accept-btn.iubenda-cs-btn-primary"
        )
        accept_cookies_button.click()
        return self

    @log_call
    def login(self) -> PolimiLoginPage:
        accedi_button = self._driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"].green:not(.pull-right)'
        )
        accedi_button.click()
        return PolimiLoginPage(self._driver)


class Bot:
    def __init__(self):
        self._driver = self._initialize_driver()

        self._logger = logger

        self._booking_outcome_reporter = BookingOutcomeReporter()

    def start(self, booking_preferences: BookingPreferences):
        self._logger.info(MESSAGES["action_begin"])

        try:
            if self._should_book_today(list(booking_preferences)):
                self._book(booking_preferences)
            else:
                self._logger.info(MESSAGES["skip_today"])
        except Exception as e:
            self._logger.info(MESSAGES["error"].format(error=e))

            self._booking_outcome_reporter.report_failure(
                e, self._driver.get_screenshot_as_png()
            )
        finally:
            self._stop()

    def _stop(self):
        self._logger.info(MESSAGES["action_end"])

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
