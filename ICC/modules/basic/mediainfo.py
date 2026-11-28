"""Telegram media metadata inspector for ICC Userbot.

ICC USERBOT module.
"""
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("minfo", ".") & filters.me)
async def media_info(client: Client, message: Message):
    media_message = message.reply_to_message or message
    media = (
        media_message.document or media_message.video or media_message.audio
        or media_message.voice or media_message.video_note or media_message.animation
        or media_message.sticker or media_message.photo
    )
    if not media:
        return await message.edit_text("Reply to a Telegram media or file with `.minfo`.")
    lines = ["**ICC USERBOT • MEDIA INFO**"]
    name = getattr(media, "file_name", None)
    mime = getattr(media, "mime_type", None)
    size = getattr(media, "file_size", None)
    file_id = getattr(media, "file_id", None)
    unique_id = getattr(media, "file_unique_id", None)
    duration = getattr(media, "duration", None)
    width = getattr(media, "width", None)
    height = getattr(media, "height", None)
    for label, value in (
        ("Name", name), ("MIME type", mime),
        ("Size", f"{size:,} bytes" if size else None),
        ("Duration", f"{duration} sec" if duration else None),
        ("Dimensions", f"{width} × {height}" if width and height else None),
        ("File ID", file_id), ("Unique ID", unique_id),
        ("Message ID", media_message.id), ("Chat ID", media_message.chat.id),
    ):
        if value is not None:
            lines.append(f"**{label}:** `{value}`")
    await message.edit_text("\n".join(lines), disable_web_page_preview=True)


add_command_help("mediainfo", [[".minfo (reply)", "Show metadata and file IDs for replied Telegram media."]])
