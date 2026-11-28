"""Summarize recent media in a chat.

Feature concept adapted from LEGENDBOT file-summary plugin (GPL-3.0).
"""
from collections import Counter

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("chatfs", ".") & filters.me)
async def chat_file_summary(client: Client, message: Message):
    limit = 1000
    if len(message.command) > 1:
        try:
            limit = max(100, min(int(message.command[1]), 2000))
        except ValueError:
            return await message.edit_text("Usage: `.chatfs [100-2000]`")
    status = await message.edit_text(f"Scanning the latest {limit} messages...")
    counts = Counter()
    total_bytes = 0
    scanned = 0
    async for item in client.get_chat_history(message.chat.id, limit=limit):
        scanned += 1
        media = (
            item.photo or item.video or item.animation or item.audio or item.voice
            or item.video_note or item.document or item.sticker
        )
        if media:
            kind = (
                "Photo" if item.photo else "Video" if item.video else
                "GIF" if item.animation else "Audio" if item.audio else
                "Voice" if item.voice else "Video note" if item.video_note else
                "Sticker" if item.sticker else "Document"
            )
            counts[kind] += 1
            total_bytes += getattr(media, "file_size", 0) or 0
        if scanned % 500 == 0:
            await status.edit_text(f"Scanned {scanned}/{limit} messages...")
    lines = ["**ICC USERBOT • CHAT FILE SUMMARY**", f"Messages scanned: `{scanned}`"]
    for kind, count in counts.most_common():
        lines.append(f"{kind}: `{count}`")
    lines.append(f"Total media: `{sum(counts.values())}`")
    lines.append(f"Known media size: `{total_bytes / (1024 * 1024):.2f} MB`")
    await status.edit_text("\n".join(lines))


add_command_help("filesummary", [[".chatfs [limit]", "Count media types in the latest 100–2000 chat messages."]])
