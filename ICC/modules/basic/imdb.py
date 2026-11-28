import os

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("imdb", ".") & filters.me)
async def imdb_lookup(client: Client, message: Message):
    query = message.text.split(maxsplit=1)[1].strip() if len(message.command) > 1 else ""
    if not query:
        return await message.edit_text("Usage: `.imdb <movie or series name>`")
    api_key = os.getenv("OMDB_API_KEY")
    if not api_key:
        return await message.edit_text("Set OMDB_API_KEY on the server to enable IMDb lookup.")
    status = await message.edit_text("Searching IMDb…")
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://www.omdbapi.com/", params={"apikey": api_key, "t": query, "plot": "short"}) as response:
                data = await response.json(content_type=None)
                if response.status != 200:
                    raise RuntimeError(f"OMDb HTTP {response.status}")
        if data.get("Response") != "True":
            return await status.edit_text(data.get("Error", "No matching title found."))
        title = data.get("Title", query)
        imdb_id = data.get("imdbID", "")
        link = f"https://www.imdb.com/title/{imdb_id}/" if imdb_id else "https://www.imdb.com/"
        lines = [
            f"**{title} ({data.get('Year', 'N/A')})**",
            f"**Type:** {data.get('Type', 'N/A')}",
            f"**Genre:** {data.get('Genre', 'N/A')}",
            f"**Rating:** {data.get('imdbRating', 'N/A')} / 10",
            f"**Runtime:** {data.get('Runtime', 'N/A')}",
            f"**Director:** {data.get('Director', 'N/A')}",
            f"**Cast:** {data.get('Actors', 'N/A')}",
            f"\n{data.get('Plot', 'No plot summary available.')}",
            f"\n[Open IMDb page]({link})",
        ]
        await status.edit_text("\n".join(lines)[:3900], disable_web_page_preview=False)
    except Exception as exc:
        await status.edit_text(f"**IMDb lookup error:** `{str(exc)[:350]}`")


add_command_help("imdb", [
    [".imdb <title>", "Fetch movie/series details from OMDb (requires OMDB_API_KEY)."],
])
