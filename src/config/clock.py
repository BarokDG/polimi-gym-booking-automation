from datetime import datetime
from zoneinfo import ZoneInfo


APP_TZ = ZoneInfo("Europe/Rome")


def now() -> datetime:
    return datetime.now(tz=APP_TZ)
