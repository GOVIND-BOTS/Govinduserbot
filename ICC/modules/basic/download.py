"""Download replied Telegram media to the userbot server.

Feature adapted for ICC Userbot from the source download plugin.
"""
import os
import re

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("download", ".") & filters.me)
async def download_replied(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return await message.edit_text("Reply to Telegram media with `.download [filename]`.")
    folder = os.path.abspath("downloads")
    os.makedirs(folder, exist_ok=True)
    status = await message.edit_text("Downloading replied media...")
    path = await client.download_media(reply, file_name=folder + "/")
    if not path:
        return await status.edit_text("Download failed.")
    custom = " ".join(message.command[1:]).strip()
    if custom:
        name = os.path.basename(custom)
        name = re.sub(r"[^\w. -]", "_", name).strip(" .")
        if not name:
            name = os.path.basename(path)
        if not os.path.splitext(name)[1]:
            name += os.path.splitext(path)[1]
        target = os.path.join(folder, name)
        if os.path.abspath(target) != os.path.abspath(path):
            base, ext = os.path.splitext(target)
            index = 1
            while os.path.exists(target):
                target = f"{base}_{index}{ext}"
                index += 1
            os.replace(path, target)
            path = target
    await status.edit_text(f"**Downloaded successfully**\nFile: `{os.path.basename(path)}`\nPath: `{path}`")


add_command_help("download", [[".download [filename] (reply)", "Download replied Telegram media to the server's downloads folder."]])
