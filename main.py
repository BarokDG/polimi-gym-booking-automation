import datetime as dt
import os
import smtplib
import time
from email.message import EmailMessage
from random import gauss, randint
from typing import Self

import pyotp
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common import ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

load_dotenv()


def get_default_chrome_options() -> Options:
    options: Options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    return options


def book_time_slot(driver: WebDriver):
    # TODO: hit no when asked if you want to book another slot
    pass


class EmailBookingConfirmation:
    def __init__(self):
        self.__smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
        self.__msg = EmailMessage()
        self.__msg["Subject"] = self.__generate_email_subject()
        self.__msg["From"] = "scripty"
        self.__msg["To"] = os.environ.get("DESTINATION_EMAIL_ADDRESS")

    def send_screenshot(self, screenshot: bytes) -> Self:
        self.__msg.add_attachment(screenshot, maintype="image", subtype="png")
        self.__send_email()

    def __send_email(self):
        if not self.__has_attachment():
            raise Exception("Attachment missing")

        self.__authenticate()
        self.__smtp_server.send_message(self.__msg)
        self.__terminate_session()

    def __authenticate(self):
        self.__smtp_server.starttls()
        self.__smtp_server.login(
            os.environ.get("SMTP_EMAIL_ADDRESS"), os.environ.get("SMTP_PASSWORD")
        )

    def __terminate_session(self):
        self.__smtp_server.quit()

    def __generate_email_subject(self):
        today = dt.datetime.now().strftime("%A %B %d")
        return f"Booking for {today}"

    def __has_attachment(self):
        for part in self.__msg.walk():
            if part.get_content_disposition() == "attachment" or part.get_filename():
                return True
        return False


class Page:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self._sleep_for_a_bit()

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

    def _take_screenshot(self):
        return self.driver.get_screenshot_as_png()


class ConfirmTimeSlotPage(Page):
    def confirm(self) -> Self:
        confirm_booking_button = self.driver.find_element(
            By.ID, "btnConfirmAppointmentBooking"
        )
        confirm_booking_button.click()
        return self


class GiuratiFitCenterBookingPage(Page):
    # TODO: Make more robust, try booking a different slot if the last one is not available
    def book_time_slot(self) -> Self:
        try:
            time_slot = self.driver.find_element(
                By.CSS_SELECTOR,
                '#day-schedule-container [data-date-offset="0"] div.event-slot:last-child',
            )
            time_slot.click()
        except ElementClickInterceptedException:
            pass

        return self

    def __get_available_time_slots(self):
        time_slots = self.driver.find_elements(
            By.CSS_SELECTOR,
            '#day-schedule-container [data-date-offset="0"] div.event-slot.slot-available',
        )
        return time_slots


class NewBookingPage(Page):
    def select_giurati_fit_center(self) -> Self:
        fit_center_booking_button = self.driver.find_element(
            By.CSS_SELECTOR, ".list-group-item:last-child"
        )
        fit_center_booking_button.click()
        return self


class BookingsPage(Page):
    def new_booking(self) -> Self:
        new_booking_button = self.driver.find_element(
            By.CSS_SELECTOR, ".purple-plum.btn_nuovaprenotazione.standard-booking.btn"
        )
        new_booking_button.click()
        return self


class DashboardPage(Page):
    def go_to_bookings(self) -> Self:
        bookings_page_button = self.driver.find_element(
            By.CSS_SELECTOR, "#home_btt_booking > div"
        )
        bookings_page_button.click()
        return self


class VerifyOTPPage(Page):
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

    def login(self) -> Self:
        accedi_button = self.driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"].green:not(.pull-right)'
        )
        accedi_button.click()
        return self


def main():
    options = get_default_chrome_options()

    # so the browser doesn't close after it finishes running.
    # will still close if driver.quit() is called
    # only for development
    # options.add_experimental_option("detach", True)

    driver: WebDriver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    SportRickLoginPage(driver).login()
    PolimiLoginPage(driver).login()
    VerifyOTPPage(driver).verify()
    DashboardPage(driver).go_to_bookings()
    BookingsPage(driver).new_booking()
    NewBookingPage(driver).select_giurati_fit_center()

    # run the script every day around midnight so
    # the time slot for the current day is available to be booked
    GiuratiFitCenterBookingPage(driver).book_time_slot()

    ConfirmTimeSlotPage(driver).confirm()

    EmailBookingConfirmation().send_screenshot(Page._take_screenshot())

    # time.sleep(10)

    driver.quit()


if __name__ == "__main__":
    main()
