import os
import re
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("getc", ".") & filters.me)
async def get_channel_media(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.edit("Usage: `.getc <1-50> <channel_username_or_id>`")
    try:
        limit = int(message.command[1])
        if not 1 <= limit <= 50:
            raise ValueError
    except ValueError:
        return await message.edit("Message limit must be between 1 and 50.")
    chat_ref = message.command[2].strip()
    folder_name = re.sub(r"[^A-Za-z0-9_-]", "_", chat_ref.lstrip("@"))[:50] or "channel"
    folder = Path("downloads") / f"channel_{folder_name}"
    folder.mkdir(parents=True, exist_ok=True)
    status = await message.edit(f"Checking the latest {limit} messages…")
    downloaded = 0
    skipped = 0
    try:
        async for item in client.get_chat_history(chat_ref, limit=limit):
            if not item.media:
                continue
            try:
                path = await client.download_media(item, file_name=str(folder) + os.sep)
                if path:
                    downloaded += 1
                else:
                    skipped += 1
            except Exception:
                skipped += 1
            if downloaded % 5 == 0:
                await status.edit(f"Downloading channel media…\nSaved: {downloaded} | Skipped: {skipped}")
        await status.edit(
            f"**Channel media download finished**\nSaved: `{downloaded}`\n"
            f"Skipped: `{skipped}`\nFolder: `{folder}`"
        )
    except Exception as exc:
        await status.edit(f"**Channel download error:** `{str(exc)[:450]}`")


add_command_help("channel_download", [
    [".getc <1-50> <channel>", "Download media from the latest 1–50 messages of a channel you can access."],
])
