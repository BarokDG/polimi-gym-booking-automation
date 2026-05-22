"""Message themes for booking automation notifications."""

from enum import Enum

from attr import dataclass


class Theme(Enum):
    WARHAMMER40K = "warhammer40k"
    MEDIEVAL = "medieval"
    BASIC = "basic"


@dataclass
class Message:
    action_start: str
    action_begin: str
    action_end: str
    error: str
    should_book_today: str
    skip_today: str
    email_success_subject: str
    email_failure_subject: str
    email_success_body: str


THEMES = {
    Theme.WARHAMMER40K: Message(
        action_start="⚙️ INITIALIZING PROTOCOL '{function_name}' - FOR THE EMPEROR!",
        action_begin="🔴 ▓▓▓▓▓▓▓▓▓▓▓▓ IMPERIAL BOOKING PROTOCOL ACTIVATED ▓▓▓▓▓▓▓▓▓▓▓▓",
        action_end="⚙️ ▓▓▓▓▓▓▓▓▓▓▓▓ PROTOCOL EXECUTION TERMINATED ▓▓▓▓▓▓▓▓stadt \n",
        error="💀 CRITICAL FAILURE: The machine spirits are displeased! {error}",
        should_book_today="📡 SCANNING FOR HOSTILE ACTIVITY... The machine spirits indicate that today is a viable day for gymnasium assault. Engaging booking protocol!",
        skip_today="📡 ALERT: Hostile activity detected on this rotation. Delaying gymnaasium assault to {date}. PATIENCE, SOLDIER! The Emperor protects those who wait.",
        email_success_subject="⚡ MISSION REPORT {date} - GYMNASIUM FORTIFICATION SUCCESSFUL!",
        email_failure_subject="⚠️ MISSION FAILURE - Gymnasium Assault Repelled on {date}",
        email_success_body=(
            "IMPERIAL CITIZEN,\n\n"
            "The Emperor's will has been done! The gymnasium stronghold has been secured for tactical combat training.\n\n"
            "Prepare your physique for battle! On {date}, you shall test your genetic enhancement against the iron gods. "
            "Pump your flesh with the fury of a thousand suns, and let your biceps become as mighty as the Emperor's throne itself!\n\n"
            "IN NOMINE IMPERATOR - GO FORTH AND CLEANSE THY BODY OF WEAKNESS!"
        ),
    ),
    Theme.MEDIEVAL: Message(
        action_start="🏰 Hark! The quest '{function_name}' doth commence...",
        action_begin="⚔️  ════════════ The Great Booking Quest Commences ════════════",
        action_end="⚔️  ════════════ The Quest Hath Concluded ════════════ \n",
        error="💥 Alas! An error hath befallen our quest: {error}",
        should_book_today="🔮 The stars align favorably! Today is a day of destiny for gymnasium conquest. Onward to battle!",
        skip_today="⏳ Patience, noble warrior! Today is not the day for battle. The quest shall commence when the stars align for thy chosen days.",
        email_success_subject="⚔️ Victory! To Battle on {date} - The Gymnasium Awaits Thy Conquest!",
        email_failure_subject="🏰 Alas! The Quest Hath Fallen Short for {date}",
        email_success_body=(
            "By thy royal command, the deed is done, my liege! The gymnasium hath been secured for thee.\n\n"
            "On the appointed day, steel thyself for glorious battle! Let thy muscles be tempered like fine blades, "
            "and thy spirit burn bright as the forge. The weights shall be thy worthy adversaries, and victory shall be thine.\n\n"
            "Go forth and conquer, noble champion! May thy gains be plentiful and thy form be mighty!"
        ),
    ),
    Theme.BASIC: Message(
        action_start="Starting function: {function_name}",
        action_begin="Starting booking automation...",
        action_end="Booking automation completed.\n",
        error="An error occurred: {error}",
        should_book_today="Today is a scheduled booking day.",
        skip_today="Today is not a scheduled booking day. Will try again tomorrow.",
        email_success_subject="Booking Successful for {date}",
        email_failure_subject="Booking Failed for {date}",
        email_success_body=(
            "The gym booking has been successfully completed.\n\n"
            "Please check your account for the confirmed booking on {date}.\n\n"
            "Thank you!"
        ),
    ),
}

# Select the active theme (change this to Theme.BASIC or Theme.WARHAMMER40K for other themes)
DEFAULT_THEME = Theme.WARHAMMER40K
MESSAGES = THEMES[DEFAULT_THEME]
