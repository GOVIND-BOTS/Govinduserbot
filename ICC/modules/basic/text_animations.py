import asyncio
import random
import time

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, MessageNotModified

from ICC.modules.help import add_command_help


async def _safe_edit(message, text):
    try:
        await message.edit_text(text)
        return True
    except MessageNotModified:
        return True
    except FloodWait as exc:
        await asyncio.sleep(exc.value)
        try:
            await message.edit_text(text)
            return True
        except Exception:
            return False
    except Exception:
        return False


def _get_argument(message):
    parts = (message.text or "").split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""


@Client.on_message(filters.command("animate", ".") & filters.me)
async def animate_text(_, message):
    text = _get_argument(message)
    if not text:
        return await message.edit_text("Usage: `.animate <text>`")
    if len(text) > 120:
        return await message.edit_text("Please keep the text under 120 characters.")

    output = await message.reply_text("⏳")
    for index in range(1, len(text) + 1):
        if not await _safe_edit(output, text[:index]):
            break
        await asyncio.sleep(0.12)


@Client.on_message(filters.command("spinner", ".") & filters.me)
async def spinner(_, message):
    argument = _get_argument(message)
    try:
        total = int(argument) if argument else 5
    except ValueError:
        return await message.edit_text("Usage: `.spinner [seconds]`")

    total = max(1, min(total, 30))
    frames = ["|", "/", "—", "\\"]
    output = await message.reply_text("⏳ Starting spinner…")
    start = time.monotonic()
    index = 0

    while time.monotonic() - start < total:
        if not await _safe_edit(output, f"{frames[index % len(frames)]} spinning…"):
            break
        index += 1
        await asyncio.sleep(0.35)

    await _safe_edit(output, "✅ Done!")


@Client.on_message(filters.command("matrix", ".") & filters.me)
async def matrix(_, message):
    argument = _get_argument(message)
    try:
        total = int(argument) if argument else 5
    except ValueError:
        return await message.edit_text("Usage: `.matrix [seconds]`")

    total = max(1, min(total, 15))
    output = await message.reply_text("Loading Matrix…")
    start = time.monotonic()

    while time.monotonic() - start < total:
        frame = "\n".join(
            "".join(random.choice("01 ") for _ in range(18))
            for _ in range(6)
        )
        if not await _safe_edit(output, f"`\n{frame}\n`"):
            break
        await asyncio.sleep(0.7)

    await _safe_edit(output, "🔚 Matrix end")


@Client.on_message(filters.command("hearts", ".") & filters.me)
async def hearts(_, message):
    text = _get_argument(message)
    if not text:
        return await message.edit_text("Usage: `.hearts <text>`")
    if len(text) > 150:
        return await message.edit_text("Please keep the text under 150 characters.")

    output = await message.reply_text(f"💖 {text} 💖")
    frames = ["💘", "💕", "💞", "💓"]
    for index in range(8):
        if not await _safe_edit(output, f"{frames[index % len(frames)]} {text} {frames[index % len(frames)]}"):
            break
        await asyncio.sleep(0.6)
    await _safe_edit(output, f"💖 {text} 💖")


@Client.on_message(filters.command("countdown", ".") & filters.me)
async def countdown(_, message):
    argument = _get_argument(message)
    try:
        start_number = int(argument)
    except ValueError:
        return await message.edit_text("Usage: `.countdown <1-60>`")

    if not 1 <= start_number <= 60:
        return await message.edit_text("Choose a number between 1 and 60.")

    output = await message.reply_text(str(start_number))
    for number in range(start_number - 1, -1, -1):
        await asyncio.sleep(1)
        if not await _safe_edit(output, str(number)):
            return
    await asyncio.sleep(0.5)
    await _safe_edit(output, "🎉 Boom!")


@Client.on_message(filters.command("wave", ".") & filters.me)
async def wave(_, message):
    text = _get_argument(message)
    if not text:
        return await message.edit_text("Usage: `.wave <text>`")
    if len(text) > 80:
        return await message.edit_text("Please keep the text under 80 characters.")

    output = await message.reply_text(text)
    width = min(len(text) + 4, 30)
    direction = 1
    position = 0

    for _ in range(width * 2):
        if not await _safe_edit(output, (" " * position) + text):
            break
        if position >= width:
            direction = -1
        elif position <= 0:
            direction = 1
        position += direction
        await asyncio.sleep(0.15)

    await _safe_edit(output, text)


add_command_help("text_animations", [
    [".animate <text>", "Animate text one character at a time."],
    [".spinner [seconds]", "Show a rotating spinner (up to 30 seconds)."],
    [".matrix [seconds]", "Show a text Matrix animation (up to 15 seconds)."],
    [".hearts <text>", "Show your text surrounded by animated hearts."],
    [".countdown <1-60>", "Count down to zero and finish with Boom."],
    [".wave <text>", "Move your text left and right."],
])
