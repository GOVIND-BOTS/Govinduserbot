"""AniList search and random anime quote utilities."""
import aiohttp
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

API = "https://graphql.anilist.co"
QUERY = """query ($search: String) { Media(search: $search, type: ANIME) { title { romaji english } siteUrl episodes averageScore status description(asHtml: false) } }"""

@Client.on_message(filters.command(["anime", "anilist"], ".") & filters.me)
async def anime_search(_, message):
    term = " ".join(message.command[1:]).strip()
    if not term:
        return await message.edit("Usage: `.anime <anime title>`")
    status = await message.edit("Searching AniList...")
    try:
        timeout = aiohttp.ClientTimeout(total=18)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(API, json={"query": QUERY, "variables": {"search": term}}) as resp:
                resp.raise_for_status()
                payload = await resp.json()
        media = payload.get("data", {}).get("Media")
        if not media:
            return await status.edit("No anime found.")
        title = media.get("title") or {}
        desc = (media.get("description") or "No description available.").replace("<br>", " ")
        desc = desc[:700]
        text = (f"**{title.get('english') or title.get('romaji') or term}**\n"
                f"**Episodes:** {media.get('episodes') or 'Unknown'} | **Score:** {media.get('averageScore') or 'N/A'}/100\n"
                f"**Status:** {media.get('status') or 'Unknown'}\n\n{desc}\n\n[Open AniList]({media.get('siteUrl')})")
        await status.edit(text, disable_web_page_preview=True)
    except Exception as exc:
        await status.edit(f"AniList request failed: `{exc}`")

@Client.on_message(filters.command("aq", ".") & filters.me)
async def anime_quote(_, message):
    status = await message.edit("Fetching an anime quote...")
    try:
        timeout = aiohttp.ClientTimeout(total=12)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://animechan.io/api/v1/quotes/random") as resp:
                resp.raise_for_status()
                data = await resp.json()
        quote = data.get("data", data)
        await status.edit(f"**{quote.get('anime', {}).get('name', 'Anime')}**\n"
                          f"**{quote.get('character', {}).get('name', 'Character')}**\n\n"
                          f"_{quote.get('content', quote.get('quote', 'No quote returned.'))}_")
    except Exception as exc:
        await status.edit(f"Quote API unavailable: `{exc}`")

add_command_help("legend_anime", [[".anime <title>", "Search anime details on AniList."], [".anilist <title>", "Search anime details on AniList."], [".aq", "Get a random anime quote."]])
