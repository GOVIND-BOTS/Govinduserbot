"""Search safe wallpapers using the Wallhaven public API.

Feature concept adapted from LEGENDBOT wallpaper plugin (GPL-3.0).
"""
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("wall", ".") & filters.me)
async def wallpaper_search(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("Usage: `.wall <query> [; count]`")
    raw = message.text.split(maxsplit=1)[1]
    parts = [part.strip() for part in raw.split(";")]
    query = parts[0]
    try:
        count = max(1, min(int(parts[1]), 5)) if len(parts) > 1 else 1
    except ValueError:
        return await message.edit_text("Count must be between 1 and 5.")
    status = await message.edit_text("Searching wallpapers...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://wallhaven.cc/api/v1/search",
                params={"q": query, "purity": "100", "sorting": "relevance", "page": 1},
                timeout=25,
            ) as response:
                data = await response.json(content_type=None)
        results = data.get("data", [])
        if not results:
            return await status.edit_text("No safe wallpapers found for that query.")
        for item in results[:count]:
            await client.send_photo(message.chat.id, item["path"], caption=f"Wallpaper: {query}")
        await status.delete()
    except Exception as exc:
        await status.edit_text(f"Wallpaper search failed: `{str(exc)[:250]}`")


add_command_help("wall", [[".wall <query> [; count]", "Search and send up to 5 SFW wallpapers."]])
