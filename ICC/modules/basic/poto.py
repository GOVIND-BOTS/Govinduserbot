"""Fetch profile photos for a user or chat.

Feature concept adapted from LEGENDBOT profile-photo plugin (GPL-3.0).
"""
import os
import tempfile

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("poto", ".") & filters.me)
async def profile_photo(client: Client, message: Message):
    target = message.reply_to_message.from_user.id if message.reply_to_message and message.reply_to_message.from_user else message.chat.id
    count = 1
    if len(message.command) > 1:
        if message.command[1].lower() == "all":
            count = 5
        else:
            try:
                count = max(1, min(int(message.command[1]), 5))
            except ValueError:
                return await message.edit_text("Usage: `.poto [1-5|all]` or reply to a user.")
    status = await message.edit_text("Fetching profile photo...")
    sent = 0
    with tempfile.TemporaryDirectory() as folder:
        async for photo in client.get_chat_photos(target, limit=count):
            path = await client.download_media(photo.big_file_id, file_name=os.path.join(folder, f"profile_{sent}.jpg"))
            if path:
                await client.send_photo(message.chat.id, path, caption="ICC USERBOT • Profile photo")
                sent += 1
    if sent:
        await status.delete()
    else:
        await status.edit_text("No profile photos found.")


add_command_help("poto", [[".poto [1-5|all] (reply)", "Get profile photos for the replied user or current chat."]])
