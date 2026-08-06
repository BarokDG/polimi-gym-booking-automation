import logging
import os

LOG_FILE = os.environ.get("LOG_FILE", "booking_automation.log")

handlers: list[logging.Handler] = [logging.StreamHandler()]

try:
    handlers.append(logging.FileHandler(LOG_FILE))
except OSError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=handlers,
)

logger = logging.getLogger(__name__)
