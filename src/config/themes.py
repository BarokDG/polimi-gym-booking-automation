"""Message themes for booking automation notifications."""

from enum import Enum

from attr import dataclass


class Theme(Enum):
    BASIC = "basic"
    CLASSICAL = "classical"
    GAME_OF_THRONES = "game_of_thrones"
    MEDIEVAL = "medieval"
    NASA = "nasa"
    STAR_WARS = "star_wars"
    WARHAMMER40K = "warhammer40k"


@dataclass
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


THEMES = {
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
    Theme.CLASSICAL: Message(
        action_start="🏛️ Ave! The discourse on '{function_name}' commences in the agora.",
        action_begin="⚱️  ════════════ The Olympic Trials Have Begun ════════════",
        action_end="⚱️  ════════════ The Contest Hath Concluded ════════════ \n",
        email_success_body=(
            "Greetings, noble citizen of Athens!\n\n"
            "The Muses have blessed you! Your gymnasium session has been secured for {date}.\n\n"
            "On that glorious day, channel the spirit of the ancient Olympians! Let your muscles grow strong like marble columns, "
            "and your determination burn bright as the sacred flame. Train as Plato philosophized: with vigor and excellence. "
            "Let each rep be a symphony, each set a sonnet to the gods!\n\n"
            "Arete—strive for excellence! The gods watch and approve!"
        ),
        email_success_subject="🏆 Your Olympic Destiny Awaits on {date} - Carpe Diem!",
        email_failure_subject="⚱️ The Fates Were Not Kind - Booking Failed for {date}",
        error="🔥 Alas! The fates have conspired against us: {error}",
        should_book_today="🏛️ The Oracle's prophecy speaks true! Today the gymnasium calls to you, as Heracles heard the call to glory!",
        skip_today="📜 The stars decree that this day is not for your trials. Return on {date}, when Nike smiles upon your endeavors.",
    ),
    Theme.GAME_OF_THRONES: Message(
        action_start="🐉 Winter is Coming... The quest '{function_name}' begins.",
        action_begin="⚔️  ════════════ The Iron Throne of Fitness Awaits ════════════",
        action_end="⚔️  ════════════ Another Day in the Great Fitness War ════════════ \n",
        email_success_body=(
            "Hear me, noble warrior of the Seven Kingdoms!\n\n"
            "The Red Priestess smiles upon you! Your gym session has been claimed for {date}.\n\n"
            "On the day written in the stars, ascend the Iron Throne of Fitness and prove your worth! "
            "Let your muscles burn like dragonfire, and your resolve be as unbreakable as the Wall itself. "
            "The Lannisters may spend their gold, but YOU shall spend your sweat and emerge victorious!\n\n"
            "Winter is coming, but your gains are eternal. WINTER IS HERE!"
        ),
        email_success_subject="⚔️ You Shall Claim the Iron Throne of Fitness on {date}!",
        email_failure_subject="💀 Winter Has Come - Booking Failed for {date}",
        error="💀 Valar Dohaeris! An error has struck us down: {error}",
        should_book_today="🐉 The ravens have spoken! The omens favor your training today. Seize your destiny and claim victory at the gymnasium!",
        skip_today="👑 Not today, warrior. The Lannisters await on a more fortuitous day. Your next battle shall commence on {date}.",
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
        action_begin="🛰️  ════════════ T-MINUS 10... 9... 8... GYMNASIUM PROTOCOL ACTIVATED ════════════",
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
        skip_today="📡 Stand down, astronaut. Gravitational forces misaligned for training today. Commence operations on {date}. Mission abort confirmed.",
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
        skip_today="🌌 The Dark Side grows strong. Today is not your battle day. Patience, Jedi. Return on {date} when the Force guides you.",
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
        skip_today="📡 ALERT: Hostile activity detected on this rotation. Delaying gymnaasium assault to {date}. PATIENCE, SOLDIER! The Emperor protects those who wait.",
    ),
}

DEFAULT_THEME = Theme.WARHAMMER40K
MESSAGES = THEMES[DEFAULT_THEME]
