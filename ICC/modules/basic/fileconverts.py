"""Convert replied static images between common formats.

Feature adapted for ICC Userbot from the source file-conversion plugin.
"""
import asyncio
import os
import tempfile

from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


def _convert(source, target, fmt):
    with Image.open(source) as image:
        if fmt == "JPEG":
            image = image.convert("RGB")
        elif fmt in ("PNG", "WEBP"):
            image = image.convert("RGBA")
        image.save(target, format=fmt)


async def _convert_reply(client, message, fmt, extension):
    reply = message.reply_to_message
    if not reply or not (reply.photo or reply.document or reply.sticker):
        return await message.edit_text(f"Reply to a static image with `.{extension}`.")
    status = await message.edit_text("Converting image...")
    with tempfile.TemporaryDirectory() as folder:
        source = await client.download_media(reply, file_name=folder + "/")
        target = os.path.join(folder, "converted." + extension)
        try:
            await asyncio.to_thread(_convert, source, target, fmt)
        except Exception as exc:
            return await status.edit_text(f"Conversion failed: {str(exc)[:200]}")
        await client.send_document(message.chat.id, target, caption=f"Converted to {fmt}.")
    await status.delete()


@Client.on_message(filters.command("png", ".") & filters.me)
async def to_png(client: Client, message: Message):
    await _convert_reply(client, message, "PNG", "png")


@Client.on_message(filters.command("jpg", ".") & filters.me)
async def to_jpg(client: Client, message: Message):
    await _convert_reply(client, message, "JPEG", "jpg")


@Client.on_message(filters.command("webp", ".") & filters.me)
async def to_webp(client: Client, message: Message):
    await _convert_reply(client, message, "WEBP", "webp")


add_command_help("fileconverts", [
    [".png (reply)", "Convert a replied static image to PNG."],
    [".jpg (reply)", "Convert a replied static image to JPEG."],
    [".webp (reply)", "Convert a replied static image to WEBP."],
])
