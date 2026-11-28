"""Retrieve a Telegram media thumbnail for ICC Userbot.

ICC USERBOT module.
"""
import os
import tempfile

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("getthumb", ".") & filters.me)
async def get_thumbnail(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return await message.edit_text("Reply to a video, document, animation or sticker with `.getthumb`.")
    media = reply.document or reply.video or reply.animation or reply.audio or reply.sticker
    thumbs = getattr(media, "thumbs", None) if media else None
    if not thumbs:
        return await message.edit_text("No separate thumbnail is available for this media.")
    status = await message.edit_text("Fetching thumbnail...")
    with tempfile.TemporaryDirectory() as folder:
        path = await client.download_media(thumbs[-1].file_id, file_name=os.path.join(folder, "thumb.jpg"))
        if not path:
            return await status.edit_text("Could not download the thumbnail.")
        await client.send_photo(message.chat.id, path, caption="ICC USERBOT • Thumbnail")
    await status.delete()


add_command_help("thumbnail", [[".getthumb (reply)", "Fetch the thumbnail of replied Telegram media."]])
