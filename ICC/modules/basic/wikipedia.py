import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("wiki", ".") & filters.me)
async def wikipedia_search(client: Client, message: Message):
    query = message.text.split(maxsplit=1)[1].strip() if len(message.command) > 1 else ""
    if not query and message.reply_to_message:
        query = message.reply_to_message.text or message.reply_to_message.caption or ""
    if not query:
        return await message.edit_text("Usage: `.wiki <topic>`")
    status = await message.edit_text("Searching Wikipedia…")
    params = {"action": "query", "generator": "search", "gsrsearch": query,
              "gsrlimit": 1, "prop": "extracts|info", "exintro": 1,
              "explaintext": 1, "inprop": "url", "format": "json"}
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://en.wikipedia.org/w/api.php", params=params) as response:
                data = await response.json(content_type=None)
                if response.status != 200:
                    raise RuntimeError(f"Wikipedia HTTP {response.status}")
        pages = data.get("query", {}).get("pages", {})
        if not pages:
            return await status.edit_text("No Wikipedia article found.")
        page = next(iter(pages.values()))
        title = page.get("title", query)
        extract = (page.get("extract") or "No summary available.").strip()
        url = page.get("fullurl") or "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")
        await status.edit_text(
            f"**{title}**\n\n{extract[:3300]}\n\n[Read on Wikipedia]({url})",
            disable_web_page_preview=True,
        )
    except Exception as exc:
        await status.edit_text(f"**Wikipedia error:** `{str(exc)[:350]}`")


add_command_help("wikipedia", [
    [".wiki <topic>", "Search Wikipedia and show the article introduction."],
])
