from urllib.parse import quote_plus
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

@Client.on_message(filters.command("app", ".") & filters.me)
async def app_search(_, message):
    query = " ".join(message.command[1:]).strip()
    if not query and message.reply_to_message:
        query = message.reply_to_message.text or ""
    if not query:
        return await message.edit("Usage: `.app <app name>`")
    url = "https://play.google.com/store/search?q=" + quote_plus(query) + "&c=apps"
    await message.edit(f"**Google Play search:** [{query}]({url})", disable_web_page_preview=True)

add_command_help("app", [[".app <name>", "Search for an app on Google Play Store."]])
