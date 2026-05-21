"""Configuration package for gym booking automation."""

from config.booking import (
    BOOKING_PREFERENCES,
    BookingPreferences,
    Day,
)
from config.themes import MESSAGES, Theme, THEMES, DEFAULT_THEME

__all__ = [
    # Booking configuration
    "Day",
    "BookingPreferences",
    "BOOKING_PREFERENCES",
    # Themes configuration
    "Theme",
    "THEMES",
    "DEFAULT_THEME",
    "MESSAGES",
]
