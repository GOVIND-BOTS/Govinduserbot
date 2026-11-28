from urllib.parse import quote_plus
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

SEARCHES = {
    "lmg": ("Google", "https://www.google.com/search?q={}"),
    "lmy": ("YouTube", "https://www.youtube.com/results?search_query={}"),
    "ddg": ("DuckDuckGo", "https://duckduckgo.com/?q={}"),
    "lmalt": ("AltNews", "https://www.altnews.in/?s={}"),
    "lmwiki": ("Wikipedia", "https://en.wikipedia.org/w/index.php?search={}"),
}

@Client.on_message(filters.command(list(SEARCHES), ".") & filters.me)
async def search_shortcuts(_, message):
    command = message.command[0].lower()
    query = " ".join(message.command[1:]).strip()
    if not query and message.reply_to_message:
        query = message.reply_to_message.text or message.reply_to_message.caption or ""
    if not query:
        return await message.edit(f"Usage: `.{command} <search query>`")
    label, template = SEARCHES[command]
    await message.edit(f"Search {label}: [{query}]({template.format(quote_plus(query))})", disable_web_page_preview=True)

add_command_help("search", [[f".{cmd} <query>", f"Search the query with {label}."] for cmd, (label, _) in SEARCHES.items()])
