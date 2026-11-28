# 100 Love You ASCII-art styles for ICC Userbot.

import random

from pyrogram import Client, filters
from ICC.modules.help import add_command_help


# Ten different layouts, each combined with ten decorative frames = 100 styles.
_LAYOUTS = [
    "      ❤️  ❤️\n    ❤️      ❤️\n   ❤️  LOVE  ❤️\n    ❤️  YOU ❤️\n      ❤️❤️❤️",
    "╭──────────────╮\n│   I LOVE YOU │\n╰──────────────╯",
    "      .-========-.\n     /  LOVE YOU  \\\n     \\            /\n      '-========-'",
    "♥══════♥══════♥\n     I LOVE YOU\n♥══════♥══════♥",
    "   *     .   *\n      LOVE\n        YOU\n   *     .   *",
    "╔══════════════╗\n║   LOVE YOU   ║\n╚══════════════╝",
    "      (\\_/ )\n      ( •ᴗ•)  ♥\n      / >💗   LOVE YOU",
    "  ┌───୨♡୧───┐\n      LOVE YOU\n  └───୨♡୧───┘",
    "    __  __\n   /  \\\\/  \\\n   \\      /\n    \\    /\n     \\  /\n      \\/\n   I LOVE YOU",
    "  ♥  L O V E  ♥\n       Y O U\n  ♥  F O R E V E R ♥",
]

_FRAMES = [
    ("", ""),
    ("💗✨ ", " ✨💗"),
    ("╭━━━━━━━━━━━━╮\n", "\n╰━━━━━━━━━━━━╯"),
    ("୨୧┈┈┈ ", " ┈┈┈୨୧"),
    ("🌹════ ", " ════🌹"),
    ("꧁༺ ", " ༻꧂"),
    ("♡━━━━━━━━ ", " ━━━━━━━━♡"),
    ("⋆｡°✩ ", " ✩°｡⋆"),
    ("💞「", "」💞"),
    ("༶•┈┈ ", " ┈┈•༶"),
]


def _make_styles():
    styles = []
    for layout_index, layout in enumerate(_LAYOUTS):
        for frame_index, (prefix, suffix) in enumerate(_FRAMES):
            art = f"{prefix}{layout}{suffix}" if prefix or suffix else layout
            styles.append((layout_index * len(_FRAMES) + frame_index + 1, art))
    return styles


LOVE_STYLES = _make_styles()


@Client.on_message(filters.command("love", ".") & filters.me)
async def love_art(_, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) > 1:
        value = args[1].strip().lower()
        if value in {"help", "list"}:
            await message.reply_text(
                "💗 LOVE YOU ART\n\n"
                ".love — Random love art\n"
                ".love 1 to .love 100 — Choose a style\n"
                ".love all — Show all 100 style numbers"
            )
            return
        if value == "all":
            await message.reply_text(
                "💞 100 LOVE YOU STYLES\n"
                + "   ".join(str(number) for number, _ in LOVE_STYLES)
                + "\n\nUse .love <number> to display any style."
            )
            return
        try:
            style_number = int(value)
        except ValueError:
            await message.reply_text("Use .love or .love 1-100.")
            return
        if not 1 <= style_number <= len(LOVE_STYLES):
            await message.reply_text("Style number 1 se 100 ke beech hona chahiye. 💗")
            return
        _, art = LOVE_STYLES[style_number - 1]
    else:
        style_number, art = random.choice(LOVE_STYLES)

    await message.reply_text(f"💘 LOVE YOU ART #{style_number}\n\n{art}")


add_command_help(
    "love",
    [
        [".love", "Random Love You ASCII art (100 styles)."],
        [".love 1-100", "Show a particular Love You art style."],
        [".love all", "Show all available style numbers."],
    ],
)
