"""Search and send GIFs using Giphy's public search endpoint."""
import aiohttp
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

async def _giphy_key():
    timeout = aiohttp.ClientTimeout(total=12)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get("https://giphy.com/") as resp:
            html = await resp.text()
    marker = "GIPHY_FE_WEB_API_KEY ="
    if marker not in html:
        raise RuntimeError("Giphy API key could not be found.")
    return html.split(marker, 1)[1].split("\n", 1)[0].strip().strip(";").strip().strip('"').strip("'")

@Client.on_message(filters.command("gifs", ".") & filters.me)
async def search_gifs(_, message):
    raw = message.text.split(maxsplit=1)
    if len(raw) < 2:
        return await message.edit("Usage: `.gifs <query> [; count]`")
    parts = [p.strip() for p in raw[1].split(";")]
    query = parts[0]
    try:
        count = int(parts[1]) if len(parts) > 1 else 1
    except ValueError:
        return await message.edit("Count must be a number from 1 to 5.")
    if not 1 <= count <= 5:
        return await message.edit("Count must be from 1 to 5.")
    status = await message.edit("Searching GIFs...")
    try:
        key = await _giphy_key()
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://api.giphy.com/v1/gifs/search",
                                   params={"q": query, "api_key": key, "limit": 25, "rating": "pg"}) as resp:
                resp.raise_for_status()
                data = await resp.json()
        items = data.get("data", [])
        if not items:
            return await status.edit("No GIFs found.")
        for item in items[:count]:
            url = item.get("images", {}).get("original", {}).get("url")
            if url:
                await message.reply_animation(url)
        await status.delete()
    except Exception as exc:
        await status.edit(f"GIF search failed: `{exc}`")

add_command_help("gifs", [[".gifs <query> [; count]", "Search Giphy and send 1–5 GIFs."]])
