import datetime as dt
import logging
import os
import smtplib
import time
from email.message import EmailMessage
from enum import Enum
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

load_dotenv()

IS_DEV_ENV = os.environ.get("ENV") == "dev"
SMTP_EMAIL_ADDRESS = os.environ.get("SMTP_EMAIL_ADDRESS")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
DESTINATION_EMAIL_ADDRESS = os.environ.get("DESTINATION_EMAIL_ADDRESS")
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("booking_automation.log"),
    ],
)


class Weekday(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @classmethod
    def today(cls) -> "Weekday":
        return cls(dt.datetime.today().weekday())

    @classmethod
    def day_after_tomorrow(cls) -> "Weekday":
        return cls((dt.datetime.today().weekday() + 2) % 7)


class WeekdayAvailableTimeSlots(Enum):
    SLOT_1 = {
        "label": "7:00-8:30",
        "index": 1,
    }
    SLOT_2 = {
        "label": "8:30-10:00",
        "index": 2,
    }
    SLOT_3 = {
        "label": "10:00-11:30",
        "index": 3,
    }
    SLOT_4 = {
        "label": "11:30-13:00",
        "index": 4,
    }
    SLOT_5 = {
        "label": "13:00-14:30",
        "index": 5,
    }
    SLOT_6 = {
        "label": "14:30-16:00",
        "index": 6,
    }
    SLOT_7 = {
        "label": "16:00-17:30",
        "index": 7,
    }
    SLOT_8 = {
        "label": "17:30-19:00",
        "index": 8,
    }
    SLOT_9 = {
        "label": "19:00-20:30",
        "index": 9,
    }
    SLOT_10 = {
        "label": "20:30-22:00",
        "index": 10,
    }


class WeekendAvailableTimeSlots(Enum):
    SLOT_1 = {
        "label": "9:00-10:30",
        "index": 1,
    }
    SLOT_2 = {
        "label": "10:30-12:00",
        "index": 2,
    }
    SLOT_3 = {
        "label": "12:00-13:30",
        "index": 3,
    }
    SLOT_4 = {
        "label": "13:30-15:00",
        "index": 4,
    }
    SLOT_5 = {
        "label": "15:00-16:30",
        "index": 5,
    }
    SLOT_6 = {
        "label": "16:30-18:00",
        "index": 6,
    }


BookingPreferences = dict[
    Weekday, WeekdayAvailableTimeSlots | WeekendAvailableTimeSlots
]


P = ParamSpec("P")
R = TypeVar("R")


def log_call(fn: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args, **kwds):
        logger.info(f"🏰 Hark! The quest '{fn.__name__}' doth commence...")
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
        msg["Subject"] = (
            f"⚔️ Victory! To Battle on {self._format_booking_date()} - The Gymnasium Awaits Thy Conquest!"
        )
        msg.set_content(
            "By thy royal command, the deed is done, my liege! The gymnasium hath been secured for thee.\n\n"
            "On the appointed day, steel thyself for glorious battle! Let thy muscles be tempered like fine blades, "
            "and thy spirit burn bright as the forge. The weights shall be thy worthy adversaries, and victory shall be thine.\n\n"
            "Go forth and conquer, noble champion! May thy gains be plentiful and thy form be mighty!"
        )
        msg = self._attach_screenshot(msg, screenshot)
        self._send_email(msg)

    @log_call
    def report_failure(self, error: Exception, screenshot: bytes = None):
        msg = EmailMessage()
        msg = self._set_addressing_info(msg)
        msg["Subject"] = (
            f"🏰 Alas! The Quest Hath Fallen Short for {self._format_booking_date()}"
        )
        msg.set_content(str(error))
        if screenshot is not None:
            self._attach_screenshot(msg, screenshot)
        self._send_email(msg)

    def _send_email(self, msg: EmailMessage):
        self._smtp_client.send_email(msg)

    def _format_booking_date(self):
        the_day_after_tomorrow = (dt.datetime.now() + dt.timedelta(days=2)).strftime(
            "%A %B %d"
        )
        return the_day_after_tomorrow

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
        self.driver = driver
        self._sleep_for_a_bit()

    def take_screenshot(self):
        return self.driver.get_screenshot_as_png()

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
        confirm_booking_button = self.driver.find_element(
            By.ID, "btnConfirmAppointmentBooking"
        )
        confirm_booking_button.click()
        return self

    @log_call
    def say_no_to_booking_another_slot(self) -> "DashboardPage":
        self._sleep_for_a_bit()
        no_button = self.driver.find_element(
            By.CSS_SELECTOR, '#srModal_g_confirm_dialog [data-modalrole="cancel"]'
        )
        no_button.click()
        return DashboardPage(self.driver)


class GiuratiFitCenterBookingPage(Page):
    # TODO: Make more robust, try booking a different slot if the prefered one is not available, etc.
    @log_call
    def book_time_slot(
        self, booking_preferences: BookingPreferences
    ) -> ConfirmTimeSlotPage:
        self._sleep_for_a_bit()
        time_slot_index = self._get_time_slot_index(booking_preferences)
        # data-date-offset 2 because we want to book for two days in advance
        time_slot = self.driver.find_element(
            By.CSS_SELECTOR,
            f'#day-schedule-container [data-date-offset="2"] div.event-slot:nth-child({time_slot_index})',
        )
        time_slot.click()
        return ConfirmTimeSlotPage(self.driver)

    def _get_time_slot_index(self, booking_preferences: BookingPreferences) -> int:
        """Get the time slot index for the day after tomorrow, because that's when we want to book for."""
        return booking_preferences.get(Weekday.day_after_tomorrow()).value["index"]


class NewBookingPage(Page):
    @log_call
    def select_giurati_fit_center(self) -> GiuratiFitCenterBookingPage:
        fit_center_booking_button = self.driver.find_element(
            By.CSS_SELECTOR, ".list-group-item:last-child"
        )
        fit_center_booking_button.click()
        return GiuratiFitCenterBookingPage(self.driver)


class BookingsPage(Page):
    @log_call
    def new_booking(self) -> NewBookingPage:
        new_booking_button = self.driver.find_element(
            By.CSS_SELECTOR, ".purple-plum.btn_nuovaprenotazione.standard-booking.btn"
        )
        new_booking_button.click()
        return NewBookingPage(self.driver)


class DashboardPage(Page):
    @log_call
    def accept_cookies(self) -> Self:
        """Need this because the accept cookies button sits on top of some of the time slots and could raise an ElementClickInterceptedException."""
        accept_cookies_button = self.driver.find_element(
            By.CSS_SELECTOR, ".iubenda-cs-accept-btn.iubenda-cs-btn-primary"
        )
        accept_cookies_button.click()
        return self

    @log_call
    def go_to_bookings(self) -> BookingsPage:
        bookings_page_button = self.driver.find_element(
            By.CSS_SELECTOR, "#home_btt_booking > div"
        )
        bookings_page_button.click()
        return BookingsPage(self.driver)

    @log_call
    def take_screenshot(self):
        self._is_loaded()
        return super().take_screenshot()

    def _is_loaded(self):
        return (
            self.driver.find_element(
                By.CSS_SELECTOR, "#event-repository > .event-main-block.row"
            )
            is not None
        )


class VerifyOTPPage(Page):
    @log_call
    def verify(self) -> DashboardPage:
        self._input_otp()
        self._click_verify_otp()
        return DashboardPage(self.driver)

    def _input_otp(self):
        otp_input = self.driver.find_element(By.ID, "otp")
        self._fill_form_input_like_a_human(otp_input, self._generate_otp())

    def _click_verify_otp(self):
        continue_button = self.driver.find_element(By.ID, "submit-dissms")
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
        return VerifyOTPPage(self.driver)

    def _input_username(self):
        username_input = self.driver.find_element(By.ID, "login")
        self._fill_form_input_like_a_human(username_input, USERNAME)

    def _input_password(self):
        password_input = self.driver.find_element(By.ID, "password")
        self._fill_form_input_like_a_human(password_input, PASSWORD)

    def _click_login(self):
        login_button_container = self.driver.find_element(
            By.CLASS_NAME, "aunicalogin-button-accedi"
        )
        login_button = login_button_container.find_element(By.TAG_NAME, "button")
        login_button.click()


class SportRickLoginPage(Page):
    _page_address = "https://ecomm.sportrick.com/sportpolimi"

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(self._page_address)

    @log_call
    def accept_cookies(self) -> Self:
        """Need this because the accept cookies button sits on top of some of the time slots and could raise an ElementClickInterceptedException."""
        accept_cookies_button = self.driver.find_element(
            By.CSS_SELECTOR, ".iubenda-cs-accept-btn.iubenda-cs-btn-primary"
        )
        accept_cookies_button.click()
        return self

    @log_call
    def login(self) -> PolimiLoginPage:
        accedi_button = self.driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"].green:not(.pull-right)'
        )
        accedi_button.click()
        return PolimiLoginPage(self.driver)


class Bot:
    def __init__(self):
        self.driver = self._initialize_driver()

        self.logger = logger

        self.booking_outcome_reporter = BookingOutcomeReporter()

    def start(self, booking_preferences: BookingPreferences):
        self.logger.info(
            "⚔️  ════════════ The Great Booking Quest Commences ════════════"
        )

        try:
            self._book(booking_preferences)
        except Exception as e:
            self.logger.info(f"💥 Alas! An error hath befallen our quest: {e}")

            self.booking_outcome_reporter.report_failure(
                e, self.driver.get_screenshot_as_png()
            )
        finally:
            self._stop()

    def _stop(self):
        self.logger.info("⚔️  ════════════ The Quest Hath Concluded ════════════ \n")

        if not IS_DEV_ENV:
            self.driver.quit()

    def _book(self, booking_preferences: BookingPreferences):
        if not self._should_book_today(list(booking_preferences)):
            return

        sport_rick_login_page = SportRickLoginPage(self.driver)
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

        self.booking_outcome_reporter.report_success(dashboard_page.take_screenshot())

    def _should_book_today(self, days_to_book_this_week: list[Weekday]) -> bool:
        """Need to adjust the days to book for, because of the offset of 2 (booking two days in advance). For example,
        on Saturday (6) we want to book for Monday (1), on Sunday (7) we want to book for Tuesday (2) and so on."""
        days_to_book_adjusted_for_offset = [
            (x.value - 2) % 7 for x in days_to_book_this_week
        ]

        today = Weekday.today().value
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
    booking_preferences: BookingPreferences = {
        Weekday.MONDAY: WeekdayAvailableTimeSlots.SLOT_10,
        Weekday.TUESDAY: WeekdayAvailableTimeSlots.SLOT_10,
        Weekday.WEDNESDAY: WeekdayAvailableTimeSlots.SLOT_10,
        Weekday.THURSDAY: WeekdayAvailableTimeSlots.SLOT_10,
        Weekday.FRIDAY: WeekdayAvailableTimeSlots.SLOT_10,
    }

    bot = Bot()
    bot.start(booking_preferences)


if __name__ == "__main__":
    main()
