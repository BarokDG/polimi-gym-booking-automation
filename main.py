from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from random import randint, gauss

from dotenv import load_dotenv

import os
import time

import pyotp

import smtplib
from email.message import EmailMessage

import datetime as dt

load_dotenv()

gym_portal_page = "https://ecomm.sportrick.com/sportpolimi"
credentials = {
    "username": os.environ.get("USERNAME"),
    "password": os.environ.get("PASSWORD"),
}


def sleep_for_a_bit(duration: int = None):
    if duration is None:
        duration = randint(1, 4)
    time.sleep(duration)


def fill_form_input_like_a_human(element: WebElement, text: str):
    mean_delay = 0.12
    std_dev = 0.04
    min_delay = 0.05

    for character in text:
        delay = max(min_delay, gauss(mean_delay, std_dev))
        element.send_keys(character)
        time.sleep(delay)


def input_username(driver: WebDriver):
    username_input = driver.find_element(By.ID, "login")
    fill_form_input_like_a_human(username_input, credentials["username"])


def input_password(driver: WebDriver):
    password_input = driver.find_element(By.ID, "password")
    fill_form_input_like_a_human(password_input, credentials["password"])


def click_login(driver: WebDriver):
    login_button_container = driver.find_element(
        By.CLASS_NAME, "aunicalogin-button-accedi"
    )
    login_button = login_button_container.find_element(By.TAG_NAME, "button")
    login_button.click()


def generate_otp():
    return pyotp.TOTP(os.environ["TOKEN"]).now()


def input_otp(driver: WebDriver):
    otp_input = driver.find_element(By.ID, "otp")
    fill_form_input_like_a_human(otp_input, generate_otp())


def click_verify_otp(driver: WebDriver):
    continue_button = driver.find_element(By.ID, "submit-dissms")
    continue_button.click()


def handle_sportrick_login(driver: WebDriver):
    accedi_button = driver.find_element(
        By.CSS_SELECTOR, 'button[type="submit"].green:not(.pull-right)'
    )
    accedi_button.click()


def log_in(driver: WebDriver):
    input_username(driver)
    input_password(driver)

    sleep_for_a_bit()

    click_login(driver)


def verify_otp(driver: WebDriver):
    input_otp(driver)

    sleep_for_a_bit()

    click_verify_otp(driver)


def get_default_chrome_options() -> Options:
    options: Options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    return options


def open_bookings_page(driver: WebDriver):
    bookings_page_button = driver.find_element(
        By.CSS_SELECTOR, "#home_btt_booking > div"
    )
    bookings_page_button.click()


def open_new_booking_page(driver: WebDriver):
    new_booking_button = driver.find_element(
        By.CSS_SELECTOR, ".purple-plum.btn_nuovaprenotazione.standard-booking.btn"
    )
    new_booking_button.click()


def open_giurati_fit_center_booking_page(driver: WebDriver):
    fit_center_booking_button = driver.find_element(
        By.CSS_SELECTOR, ".list-group-item:last-child"
    )
    fit_center_booking_button.click()


def select_time_slot(driver: WebDriver):
    time_slot = driver.find_element(
        By.CSS_SELECTOR,
        '#day-schedule-container [data-date-offset="0"] div.event-slot:last-child',
    )
    time_slot.click()


def confirm_time_slot(driver: WebDriver):
    confirm_booking_button = driver.find_element(By.ID, "btnConfirmAppointmentBooking")
    confirm_booking_button.click()


def book_time_slot(driver: WebDriver):
    select_time_slot(driver)

    sleep_for_a_bit()

    confirm_time_slot(driver)

    # TODO: hit no when asked if you want to book another slot


def get_formatted_date() -> str:
    return dt.datetime.now().strftime("%A %B %d")


def prepare_email(screenshot: bytes) -> EmailMessage:
    msg = EmailMessage()
    msg["Subject"] = f"Booking for {get_formatted_date()}"
    msg["From"] = "da server"
    msg["To"] = os.environ.get("DESTINATION_EMAIL_ADDRESS")
    msg.add_attachment(screenshot, maintype="image", subtype="png")
    return msg


def send_email(msg: EmailMessage):
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.starttls()
    smtp_server.login(
        os.environ.get("SMTP_EMAIL_ADDRESS"), os.environ.get("SMTP_PASSWORD")
    )
    smtp_server.send_message(msg)
    smtp_server.quit()


def email_screenshot(screenshot: bytes):
    email = prepare_email(screenshot)
    send_email(email)


def send_screenshot(driver: WebDriver):
    screenshot = driver.get_screenshot_as_png()
    email_screenshot(screenshot)


def main():
    options = get_default_chrome_options()

    # so the browser doesn't close after it finishes running.
    # will still close if driver.quit() is called
    # only for development
    # options.add_experimental_option("detach", True)

    driver: WebDriver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)

    driver.get(gym_portal_page)

    handle_sportrick_login(driver)

    sleep_for_a_bit()

    log_in(driver)

    sleep_for_a_bit()

    verify_otp(driver)

    sleep_for_a_bit()

    open_bookings_page(driver)

    sleep_for_a_bit()

    open_new_booking_page(driver)

    sleep_for_a_bit()

    open_giurati_fit_center_booking_page(driver)

    sleep_for_a_bit()

    # run the script every day around midnight

    book_time_slot(driver)

    sleep_for_a_bit()

    send_screenshot(driver)

    # time.sleep(10)

    driver.quit()


if __name__ == "__main__":
    main()
