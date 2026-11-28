"""Generate a simple text logo for ICC Userbot.

Feature concept adapted from LEGENDBOT logo plugin (GPL-3.0).
"""
import asyncio
import os
import tempfile
import textwrap

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


def _render_logo(text, output):
    image = Image.new("RGB", (1280, 720), (16, 22, 38))
    pixels = image.load()
    for y in range(image.height):
        blend = y / image.height
        color = (int(18 + 24 * blend), int(28 + 10 * blend), int(52 + 45 * blend))
        for x in range(image.width):
            pixels[x, y] = color
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 88)
    except OSError:
        font = ImageFont.load_default()
    lines = textwrap.wrap(text, width=18)[:3]
    heights = []
    widths = []
    for line in lines:
        box = draw.textbbox((0, 0), line, font=font, stroke_width=2)
        widths.append(box[2] - box[0])
        heights.append(box[3] - box[1])
    y = (image.height - sum(heights) - (len(lines) - 1) * 24) // 2
    for line, width, height in zip(lines, widths, heights):
        x = (image.width - width) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0))
        y += height + 24
    image.save(output, "PNG")


@Client.on_message(filters.command("logo", ".") & filters.me)
async def make_logo(client: Client, message: Message):
    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        return await message.edit_text("Usage: `.logo ICC USERBOT`")
    status = await message.edit_text("Creating logo...")
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, "icc_logo.png")
        await asyncio.to_thread(_render_logo, text[1][:100], path)
        await client.send_photo(message.chat.id, path, caption="ICC USERBOT")
    await status.delete()


add_command_help("logo", [[".logo <text>", "Create a simple custom text logo image."]])
