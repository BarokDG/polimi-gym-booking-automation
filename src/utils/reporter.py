import datetime as dt
import os
import smtplib
from email.message import EmailMessage

from ..config import BOOKING_DATE_OFFSET, MESSAGES
from .decorators import log_call

DESTINATION_EMAIL_ADDRESS = os.environ["DESTINATION_EMAIL_ADDRESS"]
SMTP_EMAIL_ADDRESS = os.environ["SMTP_EMAIL_ADDRESS"]
SMTP_PASSWORD = os.environ["SMTP_PASSWORD"]


class EmailSMTPClient:
    def __init__(self):
        self._smtp_server = smtplib.SMTP("smtp.gmail.com", 587)

    @log_call
    def send_email(self, msg: EmailMessage):
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
        msg["Subject"] = MESSAGES.email_success_subject.format(
            date=self._format_booking_date()
        )
        msg.set_content(MESSAGES.email_success_body)
        msg = self._attach_screenshot(msg, screenshot)
        self._send_email(msg)

    @log_call
    def report_failure(self, error: Exception, screenshot: bytes | None = None):
        msg = EmailMessage()
        msg = self._set_addressing_info(msg)
        msg["Subject"] = MESSAGES.email_failure_subject.format(
            date=self._format_booking_date()
        )
        msg.set_content(str(error))
        if screenshot:
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
