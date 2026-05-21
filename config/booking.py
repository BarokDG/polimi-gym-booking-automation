"""Booking preferences and time slot configuration."""

import datetime as dt
from enum import Enum


class Day(Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6

    @classmethod
    def today(cls) -> "Day":
        return cls(dt.datetime.today().weekday())

    @classmethod
    def day_after_tomorrow(cls) -> "Day":
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


BookingPreferences = dict[Day, WeekdayAvailableTimeSlots | WeekendAvailableTimeSlots]


# Booking preferences - configure here which days and time slots to book
BOOKING_PREFERENCES: BookingPreferences = {
    Day.MONDAY: WeekdayAvailableTimeSlots.SLOT_9,
    Day.TUESDAY: WeekdayAvailableTimeSlots.SLOT_9,
    Day.WEDNESDAY: WeekdayAvailableTimeSlots.SLOT_9,
    Day.THURSDAY: WeekdayAvailableTimeSlots.SLOT_9,
    Day.FRIDAY: WeekdayAvailableTimeSlots.SLOT_9,
}
