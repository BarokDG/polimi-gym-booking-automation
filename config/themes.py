"""Message themes for booking automation notifications."""

from enum import Enum


class Theme(Enum):
    WARHAMMER40K = "warhammer40k"
    MEDIEVAL = "medieval"
    BASIC = "basic"


THEMES = {
    Theme.WARHAMMER40K: {
        # Logging messages
        "action_start": "⚙️ INITIALIZING PROTOCOL '{function_name}' - FOR THE EMPEROR!",
        "action_begin": "🔴 ▓▓▓▓▓▓▓▓▓▓▓▓ IMPERIAL BOOKING PROTOCOL ACTIVATED ▓▓▓▓▓▓▓▓▓▓▓▓",
        "action_end": "⚙️ ▓▓▓▓▓▓▓▓▓▓▓▓ PROTOCOL EXECUTION TERMINATED ▓▓▓▓▓▓▓▓▓▓▓▓ \n",
        "skip_today": "📡 ALERT: Hostile activity detected on this rotation. Delaying gymnaasium assault to {date}. PATIENCE, SOLDIER! The Emperor protects those who wait.",
        "error": "💀 CRITICAL FAILURE: The machine spirits are displeased! {error}",
        # Email subjects
        "email_success_subject": "⚡ MISSION REPORT {date} - GYMNASIUM FORTIFICATION SUCCESSFUL!",
        "email_failure_subject": "⚠️ MISSION FAILURE - Gymnasium Assault Repelled on {date}",
        # Email content
        "email_success_body": (
            "IMPERIAL CITIZEN,\n\n"
            "The Emperor's will has been done! The gymnasium stronghold has been secured for tactical combat training.\n\n"
            "Prepare your physique for battle! On {date}, you shall test your genetic enhancement against the iron gods. "
            "Pump your flesh with the fury of a thousand suns, and let your biceps become as mighty as the Emperor's throne itself!\n\n"
            "IN NOMINE IMPERATOR - GO FORTH AND CLEANSE THY BODY OF WEAKNESS!"
        ),
    },
    Theme.MEDIEVAL: {
        # Logging messages
        "action_start": "🏰 Hark! The quest '{function_name}' doth commence...",
        "action_begin": "⚔️  ════════════ The Great Booking Quest Commences ════════════",
        "action_end": "⚔️  ════════════ The Quest Hath Concluded ════════════ \n",
        "skip_today": "⏳ Patience, noble warrior! Today is not the day for battle. The quest shall commence when the stars align for thy chosen days.",
        "error": "💥 Alas! An error hath befallen our quest: {error}",
        # Email subjects
        "email_success_subject": "⚔️ Victory! To Battle on {date} - The Gymnasium Awaits Thy Conquest!",
        "email_failure_subject": "🏰 Alas! The Quest Hath Fallen Short for {date}",
        # Email content
        "email_success_body": (
            "By thy royal command, the deed is done, my liege! The gymnasium hath been secured for thee.\n\n"
            "On the appointed day, steel thyself for glorious battle! Let thy muscles be tempered like fine blades, "
            "and thy spirit burn bright as the forge. The weights shall be thy worthy adversaries, and victory shall be thine.\n\n"
            "Go forth and conquer, noble champion! May thy gains be plentiful and thy form be mighty!"
        ),
    },
    Theme.BASIC: {
        # Logging messages
        "action_start": "Starting function: {function_name}",
        "action_begin": "Starting booking automation...",
        "action_end": "Booking automation completed.\n",
        "skip_today": "Today is not a scheduled booking day. Will try again tomorrow.",
        "error": "An error occurred: {error}",
        # Email subjects
        "email_success_subject": "Booking Successful for {date}",
        "email_failure_subject": "Booking Failed for {date}",
        # Email content
        "email_success_body": (
            "The gym booking has been successfully completed.\n\n"
            "Please check your account for the confirmed booking on {date}.\n\n"
            "Thank you!"
        ),
    },
}

# Select the active theme (change this to Theme.BASIC or Theme.WARHAMMER40K for other themes)
DEFAULT_THEME = Theme.MEDIEVAL
MESSAGES = THEMES[DEFAULT_THEME]
