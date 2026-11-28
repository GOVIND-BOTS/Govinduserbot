"""Render text as a simple note image for ICC Userbot.

Feature adapted for ICC Userbot from the source writer plugin.
"""
import asyncio
import io
import textwrap

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


def _render_note(text):
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 30)
    except OSError:
        font = ImageFont.load_default()
    lines = []
    for paragraph in text.splitlines() or [text]:
        lines.extend(textwrap.wrap(paragraph, width=48) or [""])
    line_height = 44
    height = max(420, 120 + len(lines) * line_height)
    height = min(height, 3600)
    image = Image.new("RGB", (1000, height), (250, 246, 226))
    draw = ImageDraw.Draw(image)
    draw.rectangle((28, 28, 972, height - 28), outline=(150, 130, 100), width=3)
    y = 75
    for line in lines[:70]:
        draw.text((75, y), line, fill=(30, 42, 65), font=font)
        y += line_height
    output = io.BytesIO()
    output.name = "icc_note.png"
    image.save(output, format="PNG")
    output.seek(0)
    return output


@Client.on_message(filters.command(["note", "write"], ".") & filters.me)
async def write_note(client: Client, message: Message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2 and message.reply_to_message and message.reply_to_message.text:
        body = message.reply_to_message.text
    elif len(text) > 1:
        body = text[1]
    else:
        return await message.edit_text("Usage: `.note <text>` or reply to text with `.note`.")
    status = await message.edit_text("Creating note image...")
    image = await asyncio.to_thread(_render_note, body[:2500])
    await client.send_photo(message.chat.id, image, caption="ICC USERBOT • Note")
    await status.delete()


add_command_help("writer", [[".note <text> (or reply)", "Render text as a simple note image."]])
