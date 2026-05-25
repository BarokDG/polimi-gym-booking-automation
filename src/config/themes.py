"""Message themes for booking automation messages and notifications."""

from enum import Enum

from attr import dataclass


class Theme(Enum):
    BASIC = "basic"
    MEDIEVAL = "medieval"
    NASA = "nasa"
    STAR_WARS = "star_wars"
    WARHAMMER40K = "warhammer40k"


@dataclass(frozen=True)
class Message:
    action_begin: str
    action_end: str
    action_start: str
    email_failure_subject: str
    email_success_body: str
    email_success_subject: str
    error: str
    should_book_today: str
    skip_today: str


THEMES: dict[Theme, Message] = {
    Theme.BASIC: Message(
        action_start="Starting function: {function_name}",
        action_begin="Starting booking automation...",
        action_end="Booking automation completed.\n",
        email_success_body=(
            "The gym booking has been successfully completed.\n\n"
            "Please check your account for the confirmed booking on {date}.\n\n"
            "Thank you!"
        ),
        email_success_subject="Booking Successful for {date}",
        email_failure_subject="Booking Failed for {date}",
        error="An error occurred: {error}",
        should_book_today="Today is a scheduled booking day.",
        skip_today="Today is not a scheduled booking day. Will try again tomorrow.",
    ),
    Theme.MEDIEVAL: Message(
        action_start="🏰 Hark! The quest '{function_name}' doth commence...",
        action_begin="⚔️  ════════════ The Great Booking Quest Commences ════════════",
        action_end="⚔️  ════════════ The Quest Hath Concluded ════════════ \n",
        email_success_body=(
            "By thy royal command, the deed is done, my liege! The gymnasium hath been secured for thee.\n\n"
            "On the appointed day, steel thyself for glorious battle! Let thy muscles be tempered like fine blades, "
            "and thy spirit burn bright as the forge. The weights shall be thy worthy adversaries, and victory shall be thine.\n\n"
            "Go forth and conquer, noble champion! May thy gains be plentiful and thy form be mighty!"
        ),
        email_success_subject="⚔️ Victory! To Battle on {date} - The Gymnasium Awaits Thy Conquest!",
        email_failure_subject="🏰 Alas! The Quest Hath Fallen Short for {date}",
        error="💥 Alas! An error hath befallen our quest: {error}",
        should_book_today="🔮 The stars align favorably! Today is a day of destiny for gymnasium conquest. Onward to battle!",
        skip_today="⏳ Patience, noble warrior! Today is not the day for battle. The quest shall commence when the stars align for thy chosen days.",
    ),
    Theme.NASA: Message(
        action_start="🚀 Mission Control: Initiating '{function_name}' launch sequence.",
        action_begin="🛰️  ════════════ T-MINUS 3... 2... 1... GYMNASIUM PROTOCOL ACTIVATED ════════════",
        action_end="🛰️  ════════════ MISSION TELEMETRY: ALL SYSTEMS NOMINAL ════════════ \n",
        email_success_body=(
            "Greetings, Astronaut!\n\n"
            "Mission Control has confirmed your fitness expedition for {date}. You are go for launch!\n\n"
            "On the appointed day, execute your gymnasium protocol with the precision of a spacewalk. "
            "Engage your thrusters (your legs), stabilize your payload (the weights), and achieve orbital velocity in your training regimen. "
            "Let your sweat be the fuel that propels you beyond the atmosphere of mediocrity!\n\n"
            "This is Mission Control, signing off. Go forth and conquer the final frontier of fitness. Over!"
        ),
        email_success_subject="🚀 MISSION BRIEFING {date} - Gym Training Sequence APPROVED!",
        email_failure_subject="⚠️ MISSION CONTROL ALERT - Training Launch Failed for {date}",
        error="⚠️  Houston, we have a problem! Error detected: {error}",
        should_book_today="🌌 All systems go! Mission Control confirms that today is optimal for orbital gym training. Stand by for launch!",
        skip_today="📡 Stand down, astronaut. Gravitational forces misaligned for training today. Mission abort confirmed.",
    ),
    Theme.STAR_WARS: Message(
        action_start="🌟 May the Force be with you... Initiating '{function_name}' sequence.",
        action_begin="⚡ ▓▓▓▓▓▓▓▓▓▓▓▓ JEDI TRAINING PROTOCOL ENGAGED ▓▓▓▓▓▓▓▓▓▓▓▓",
        action_end="⚡ ▓▓▓▓▓▓▓▓▓▓▓▓ HOLOCRON DATA TRANSFER COMPLETE ▓▓▓▓▓▓▓▓▓▓▓▓ \n",
        email_success_body=(
            "Young Padawan,\n\n"
            "The Force is strong with this one! Your gym session has been secured for {date}.\n\n"
            "On the appointed day, channel the Force through your muscles. Let the lightsaber of determination cut through weakness. "
            "Train as the great Jedi Masters have trained before you, and your body shall be transformed into an instrument of power!\n\n"
            "May the Force be with you, always!"
        ),
        email_failure_subject="🛸 Uh Oh! A Disturbance in the Force - Booking Failed for {date}",
        email_success_subject="⚡ Jedi Training Confirmed for {date} - The Force is Strong!",
        error="🛸 A disturbance in the Force! Error detected: {error}",
        should_book_today="🌌 The Force indicates that today is aligned with your destiny. Proceed to the gymnasium, young Padawan!",
        skip_today="🌌 The Dark Side grows strong. Today is not your battle day. Patience, Jedi.",
    ),
    Theme.WARHAMMER40K: Message(
        action_begin="🔴 ▓▓▓▓▓▓▓▓▓▓▓▓ IMPERIAL BOOKING PROTOCOL ACTIVATED ▓▓▓▓▓▓▓▓▓▓▓▓",
        action_end="⚙️ ▓▓▓▓▓▓▓▓▓▓▓▓ PROTOCOL EXECUTION TERMINATED ▓▓▓▓▓▓▓▓▓▓▓▓ \n",
        action_start="⚙️ INITIALIZING PROTOCOL '{function_name}' - FOR THE EMPEROR!",
        email_success_body=(
            "IMPERIAL CITIZEN,\n\n"
            "The Emperor's will has been done! The gymnasium stronghold has been secured for tactical combat training.\n\n"
            "Prepare your physique for battle! On {date}, you shall test your genetic enhancement against the iron gods. "
            "Pump your flesh with the fury of a thousand suns, and let your biceps become as mighty as the Emperor's throne itself!\n\n"
            "IN NOMINE IMPERATOR - GO FORTH AND CLEANSE THY BODY OF WEAKNESS!"
        ),
        email_failure_subject="⚠️ MISSION FAILURE - Gymnasium Assault Repelled on {date}",
        email_success_subject="⚡ MISSION REPORT {date} - GYMNASIUM FORTIFICATION SUCCESSFUL!",
        error="💀 CRITICAL FAILURE: The machine spirits are displeased! {error}",
        should_book_today="📡 SCANNING FOR HOSTILE ACTIVITY... The machine spirits indicate that today is a viable day for gymnasium assault. Engaging booking protocol!",
        skip_today="📡 ALERT: Hostile activity detected on this rotation. Delaying gymnasium assault. PATIENCE, SOLDIER! The Emperor protects those who wait.",
    ),
}

DEFAULT_THEME = Theme.BASIC
MESSAGES = THEMES[DEFAULT_THEME]
