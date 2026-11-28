import re

from pyrogram import Client, filters

from ICC.modules.help import add_command_help


FONT = {
    "a": ("01110", "10001", "11111", "10001", "10001"),
    "b": ("11110", "10001", "11110", "10001", "11110"),
    "c": ("01111", "10000", "10000", "10000", "01111"),
    "d": ("11110", "10001", "10001", "10001", "11110"),
    "e": ("11111", "10000", "11110", "10000", "11111"),
    "f": ("11111", "10000", "11110", "10000", "10000"),
    "g": ("01111", "10000", "10111", "10001", "01111"),
    "h": ("10001", "10001", "11111", "10001", "10001"),
    "i": ("11111", "00100", "00100", "00100", "11111"),
    "j": ("00111", "00010", "00010", "10010", "01100"),
    "k": ("10001", "10010", "11100", "10010", "10001"),
    "l": ("10000", "10000", "10000", "10000", "11111"),
    "m": ("10001", "11011", "10101", "10001", "10001"),
    "n": ("10001", "11001", "10101", "10011", "10001"),
    "o": ("01110", "10001", "10001", "10001", "01110"),
    "p": ("11110", "10001", "11110", "10000", "10000"),
    "q": ("01110", "10001", "10101", "10010", "01101"),
    "r": ("11110", "10001", "11110", "10010", "10001"),
    "s": ("01111", "10000", "01110", "00001", "11110"),
    "t": ("11111", "00100", "00100", "00100", "00100"),
    "u": ("10001", "10001", "10001", "10001", "01110"),
    "v": ("10001", "10001", "10001", "01010", "00100"),
    "w": ("10001", "10001", "10101", "11011", "10001"),
    "x": ("10001", "01010", "00100", "01010", "10001"),
    "y": ("10001", "01010", "00100", "00100", "00100"),
    "z": ("11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10011", "10101", "11001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00010", "00100", "11111"),
    "3": ("11110", "00001", "00110", "00001", "11110"),
    "4": ("10010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "11110"),
    "6": ("01110", "10000", "11110", "10001", "01110"),
    "7": ("11111", "00010", "00100", "01000", "01000"),
    "8": ("01110", "10001", "01110", "10001", "01110"),
    "9": ("01110", "10001", "01111", "00001", "01110"),
}

PALETTE = [
    "💖", "💗", "💛", "💙", "💟", "💚", "💜", "💖", "💗",
    "💛", "💙", "💟", "💚", "💜", "💖", "💗", "💛", "💙",
    "💟", "💚", "💜", "💖", "💗", "💛", "💙", "💟",
    "💚", "💜", "💖", "💗", "💛", "💙", "💟", "💚", "💜", "💖",
]


def _render(text, emoji_for):
    text = text.lower()
    if len(text) > 12:
        raise ValueError("Please use 12 characters or fewer.")

    rows = []
    for row_index in range(5):
        parts = []
        for char in text:
            if char == " ":
                parts.append("     ")
                continue
            pattern = FONT.get(char)
            if pattern:
                parts.append("".join(emoji_for(char, col) if bit == "1" else "　" for col, bit in enumerate(pattern[row_index])))
            else:
                parts.append("　" * 5)
        rows.append("　".join(parts).rstrip())
    return "\n".join(rows)


def _emoji_for_letter(char, col):
    index = (ord(char) - 97) % len(PALETTE) if char.isalpha() else int(char) % len(PALETTE)
    return PALETTE[(index + col) % len(PALETTE)]


@Client.on_message(filters.command("emoji", ".") & filters.me)
async def emoji_art(_, message):
    parts = (message.text or "").split(maxsplit=1)
    text = parts[1].strip() if len(parts) > 1 else ""

    if message.reply_to_message:
        replied = message.reply_to_message
        text = replied.text or replied.caption or text

    if not text:
        return await message.edit_text("Usage: `.emoji <text>` (or reply to a text message)")
    try:
        result = _render(text, lambda char, col: _emoji_for_letter(char, col))
    except ValueError as exc:
        return await message.edit_text(str(exc))

    await message.reply_text(result)


@Client.on_message(filters.command("cmoji", ".") & filters.me)
async def custom_emoji_art(_, message):
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3:
        if message.reply_to_message:
            return await message.edit_text("Usage: `.cmoji <emoji> <text>`")
        return await message.edit_text("Usage: `.cmoji <emoji> <text>`")

    emoji, text = parts[1], parts[2].strip()
    if not text:
        return await message.edit_text("Please provide text after the emoji.")

    # Accept one visible emoji (including joined/variation-selector sequences).
    if len(emoji) > 12 or re.search(r"\s", emoji):
        return await message.edit_text("Please provide a single emoji.")

    try:
        result = _render(text, lambda _char, _col: emoji)
    except ValueError as exc:
        return await message.edit_text(str(exc))

    await message.reply_text(result)


add_command_help("emojify", [
    [".emoji <text>", "Render letters and numbers using colorful emoji art."],
    [".cmoji <emoji> <text>", "Render text using your chosen emoji."],
])
