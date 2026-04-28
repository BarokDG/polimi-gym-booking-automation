import datetime as dt
from enum import Enum
import os
import smtplib
import time
from email.message import EmailMessage
from random import gauss, randint
from typing import Callable, Self

import pyotp
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()


def log_call(f: Callable) -> Callable:
    def wrapper(*args, **kwds):
        print(f"Started {f.__name__}")
        return f(*args, **kwds)

    return wrapper


class EmailSMTPClient:
    def __init__(self):
        self.__smtp_server = smtplib.SMTP("smtp.gmail.com", 587)

    @log_call
    def send_email(self, msg):
        self.__authenticate()
        self.__smtp_server.send_message(msg)
        self.__terminate_session()

    def __authenticate(self):
        self.__smtp_server.starttls()
        self.__smtp_server.login(
            os.environ.get("SMTP_EMAIL_ADDRESS"), os.environ.get("SMTP_PASSWORD")
        )

    def __terminate_session(self):
        self.__smtp_server.quit()


class EmailBookingOutcomeReporter:
    def __init__(self):
        self.__smtp_client = EmailSMTPClient()

    @log_call
    def report_success(self, screenshot: bytes):
        msg = EmailMessage()
        msg = self.__set_addressing_info(msg)
        msg["Subject"] = f"Gym successfully booked for {self.__format_booking_date()}"
        msg.set_content("I have done your bidding father")
        msg = self.__attach_screenshot(msg, screenshot)
        self.__send_email(msg)

    @log_call
    def report_failure(self, error: Exception, screenshot: bytes = None):
        msg = EmailMessage()
        msg = self.__set_addressing_info(msg)
        msg["Subject"] = f"Failed to book the gym for {self.__format_booking_date()}"
        msg.set_content(str(error))
        if screenshot is not None:
            self.__attach_screenshot(msg, screenshot)
        self.__send_email(msg)

    def __send_email(self, msg: EmailMessage):
        self.__smtp_client.send_email(msg)

    def __format_booking_date(self):
        the_day_after_tomorrow = (dt.datetime.now() + dt.timedelta(days=2)).strftime(
            "%A %B %d"
        )
        return the_day_after_tomorrow

    def __attach_screenshot(self, msg: EmailMessage, screenshot: bytes) -> EmailMessage:
        msg.add_attachment(screenshot, maintype="image", subtype="png")
        return msg

    def __set_addressing_info(
        self,
        msg: EmailMessage,
        email_from: str = "me",
        email_to: str = os.environ.get("DESTINATION_EMAIL_ADDRESS"),
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
    def say_no_to_booking_another_slot(self) -> Self:
        self._sleep_for_a_bit()
        no_button = self.driver.find_element(
            By.CSS_SELECTOR, '#srModal_g_confirm_dialog [data-modalrole="cancel"]'
        )
        no_button.click()
        return self


class GiuratiFitCenterBookingPage(Page):
    # TODO: Make more robust, try booking a different slot if the last one is not available
    @log_call
    def book_time_slot(self) -> Self:
        self._sleep_for_a_bit()
        # offset 2 because we want to book for two days in advance
        time_slot = self.driver.find_element(
            By.CSS_SELECTOR,
            '#day-schedule-container [data-date-offset="2"] div.event-slot:last-child',
        )
        time_slot.click()
        return self

    def __get_available_time_slots(self):
        time_slots = self.driver.find_elements(
            By.CSS_SELECTOR,
            '#day-schedule-container [data-date-offset="2"] div.event-slot.slot-available',
        )
        return time_slots


class NewBookingPage(Page):
    @log_call
    def select_giurati_fit_center(self) -> Self:
        fit_center_booking_button = self.driver.find_element(
            By.CSS_SELECTOR, ".list-group-item:last-child"
        )
        fit_center_booking_button.click()
        return self


class BookingsPage(Page):
    @log_call
    def new_booking(self) -> Self:
        new_booking_button = self.driver.find_element(
            By.CSS_SELECTOR, ".purple-plum.btn_nuovaprenotazione.standard-booking.btn"
        )
        new_booking_button.click()
        return self


class DashboardPage(Page):
    def is_loaded(self):
        return (
            self.driver.find_element(
                By.CSS_SELECTOR, "#event-repository > .event-main-block.row"
            )
            is not None
        )

    @log_call
    def accept_cookies(self) -> Self:
        """Need this because the accept cookies button sits on top of some of the time slots and could raise an ElementClickInterceptedException."""
        accept_cookies_button = self.driver.find_element(
            By.CSS_SELECTOR, ".iubenda-cs-accept-btn.iubenda-cs-btn-primary"
        )
        accept_cookies_button.click()
        return self

    @log_call
    def go_to_bookings(self) -> Self:
        bookings_page_button = self.driver.find_element(
            By.CSS_SELECTOR, "#home_btt_booking > div"
        )
        bookings_page_button.click()
        return self

    @log_call
    def take_screenshot(self):
        self.is_loaded()
        return super().take_screenshot()


class VerifyOTPPage(Page):
    @log_call
    def verify(self) -> Self:
        self.__input_otp()
        self.__click_verify_otp()
        return self

    def __input_otp(self):
        otp_input = self.driver.find_element(By.ID, "otp")
        self._fill_form_input_like_a_human(otp_input, self.__generate_otp())

    def __click_verify_otp(self):
        continue_button = self.driver.find_element(By.ID, "submit-dissms")
        continue_button.click()

    def __generate_otp(self) -> str:
        return pyotp.TOTP(os.environ["TOKEN"]).now()


class PolimiLoginPage(Page):
    @log_call
    def login(self) -> Self:
        self.__input_username()
        self.__input_password()
        self._sleep_for_a_bit()
        self.__click_login()
        return self

    def __input_username(self):
        username_input = self.driver.find_element(By.ID, "login")
        self._fill_form_input_like_a_human(username_input, os.environ.get("USERNAME"))

    def __input_password(self):
        password_input = self.driver.find_element(By.ID, "password")
        self._fill_form_input_like_a_human(password_input, os.environ.get("PASSWORD"))

    def __click_login(self):
        login_button_container = self.driver.find_element(
            By.CLASS_NAME, "aunicalogin-button-accedi"
        )
        login_button = login_button_container.find_element(By.TAG_NAME, "button")
        login_button.click()


class SportRickLoginPage(Page):
    __page_address = "https://ecomm.sportrick.com/sportpolimi"

    def __init__(self, driver):
        super().__init__(driver)
        self.driver.get(self.__page_address)

    @log_call
    def accept_cookies(self) -> Self:
        """Need this because the accept cookies button sits on top of some of the time slots and could raise an ElementClickInterceptedException."""
        accept_cookies_button = self.driver.find_element(
            By.CSS_SELECTOR, ".iubenda-cs-accept-btn.iubenda-cs-btn-primary"
        )
        accept_cookies_button.click()
        return self

    @log_call
    def login(self) -> Self:
        accedi_button = self.driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"].green:not(.pull-right)'
        )
        accedi_button.click()
        return self


class Weekday(Enum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6


def should_book_today():
    days_to_book_this_week = [
        Weekday.MONDAY,
        Weekday.TUESDAY,
        Weekday.WEDNESDAY,
        Weekday.THURSDAY,
        Weekday.FRIDAY,
    ]

    """Need to adjust the days to book for because of the offset of 2 (booking two days in advance), so for example 
    on Saturday (6) we want to book for Monday (1), on Sunday (0) we want to book for Tuesday (2) and so on."""
    days_to_book_adjusted_for_offset = [
        (x.value - 2) % 7 for x in days_to_book_this_week
    ]

    today = int(dt.datetime.now().strftime("%w"))
    if today not in days_to_book_adjusted_for_offset:
        return False

    return True


def get_chrome_driver_options() -> Options:
    options: Options = webdriver.ChromeOptions()

    options.add_argument("--no-sandbox")

    if os.environ.get("ENV") == "dev":
        # So the browser doesn't close after it finishes running. Will still close if driver.quit() is called.
        options.add_experimental_option("detach", True)
    else:
        # To run in VPS environments without a display
        options.add_argument("--headless")

    return options


def main():
    if not should_book_today():
        return

    driver: WebDriver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=get_chrome_driver_options(),
    )
    driver.implicitly_wait(10)

    email_booking_outcome_reporter = EmailBookingOutcomeReporter()

    try:
        SportRickLoginPage(driver).accept_cookies().login()
        PolimiLoginPage(driver).login()
        VerifyOTPPage(driver).verify()
        dashboardPage = DashboardPage(driver).accept_cookies().go_to_bookings()
        BookingsPage(driver).new_booking()
        NewBookingPage(driver).select_giurati_fit_center()
        GiuratiFitCenterBookingPage(driver).book_time_slot()
        ConfirmTimeSlotPage(driver).confirm().say_no_to_booking_another_slot()

        # dashboardPage will open after the booking is confirmed, so we can take the screenshot from there to show the successful booking
        email_booking_outcome_reporter.report_success(dashboardPage.take_screenshot())
    except Exception as e:
        email_booking_outcome_reporter.report_failure(e)

    if os.environ.get("ENV") != "dev":
        driver.quit()


if __name__ == "__main__":
    main()
