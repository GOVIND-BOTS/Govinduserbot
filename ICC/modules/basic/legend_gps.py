"""Geocode a place and send its Telegram location; inspired by LEGENDBOT."""
import aiohttp
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

@Client.on_message(filters.command("gps", ".") & filters.me)
async def gps_lookup(_, message):
    query = " ".join(message.command[1:]).strip()
    if not query and message.reply_to_message:
        query = message.reply_to_message.text or ""
    if not query:
        return await message.edit("Usage: `.gps <place>`")
    status = await message.edit("Finding location...")
    try:
        headers = {"User-Agent": "GovindUserbot/1.0 (location lookup)"}
        params = {"q": query, "format": "jsonv2", "limit": 1}
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get("https://nominatim.openstreetmap.org/search", params=params) as resp:
                resp.raise_for_status()
                results = await resp.json()
        if not results:
            return await status.edit("Location not found.")
        item = results[0]
        await message.reply_location(float(item["lat"]), float(item["lon"]))
        await status.delete()
    except Exception as exc:
        await status.edit(f"Location lookup failed: `{exc}`")

add_command_help("legend_gps", [[".gps <place>", "Find a place and send its map location."]])
