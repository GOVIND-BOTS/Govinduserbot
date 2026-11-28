"""Rename and resend a replied Telegram file.

Feature concept adapted from LEGENDBOT rename plugin (GPL-3.0).
"""
import os
import tempfile

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("rnup", ".") & filters.me)
async def rename_upload(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return await message.edit_text("Reply to a file or media: `.rnup new_name.ext`")
    if len(message.command) < 2:
        return await message.edit_text("Usage: `.rnup new_name.ext`")
    filename = os.path.basename(" ".join(message.command[1:])).strip()
    if not filename or filename in (".", ".."):
        return await message.edit_text("Please provide a valid filename.")
    status = await message.edit_text("Preparing renamed file...")
    with tempfile.TemporaryDirectory() as folder:
        path = await client.download_media(reply, file_name=os.path.join(folder, filename))
        if not path:
            return await status.edit_text("Could not download the replied media.")
        await client.send_document(
            message.chat.id, path,
            caption=f"**Renamed by ICC USERBOT**\n`{filename}`",
            reply_to_message_id=reply.id,
        )
    await status.delete()


add_command_help("rename", [[".rnup <new_name> (reply)", "Rename and resend a replied Telegram file as a document."]])
