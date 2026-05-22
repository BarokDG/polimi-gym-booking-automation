import os
import time
from abc import ABC
from random import gauss, randint
from typing import Self

import pyotp
from selenium.common import NoSuchElementException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from config import BOOKING_DATE_OFFSET, BookingPreferences, Day
from utils import log_call

USERNAME = os.environ["USERNAME"]
PASSWORD = os.environ["PASSWORD"]
TOKEN = os.environ["TOKEN"]


class Page(ABC):
    def __init__(self, driver: WebDriver):
        self._driver = driver
        self._sleep_for_a_bit()

    def take_screenshot(self):
        return self._driver.get_screenshot_as_png()

    def _sleep_for_a_bit(self, duration: int | None = None):
        if not duration:
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
        try:
            self._driver.find_element(
                By.CSS_SELECTOR, "#event-repository > .event-main-block.row"
            )
            return True
        except NoSuchElementException:
            return False


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
        return pyotp.TOTP(TOKEN).now()


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

    def __init__(self, driver: WebDriver):
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
