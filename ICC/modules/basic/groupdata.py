"""Basic group and channel information for ICC Userbot.

Feature adapted for ICC Userbot from the source group-data plugin.
"""
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("chatinfo", ".") & filters.me)
async def chat_info(client: Client, message: Message):
    target = message.chat.id
    if len(message.command) > 1:
        target = message.command[1]
    try:
        chat = await client.get_chat(target)
        count = await client.get_chat_members_count(chat.id)
    except Exception as exc:
        return await message.edit_text(f"Could not fetch chat information: `{str(exc)[:200]}`")
    lines = ["**ICC USERBOT • CHAT INFO**"]
    for label, value in (
        ("Title", chat.title), ("ID", chat.id), ("Username", f"@{chat.username}" if chat.username else None),
        ("Type", str(chat.type)), ("Members", count), ("Description", chat.description),
    ):
        if value is not None:
            lines.append(f"**{label}:** `{value}`")
    await message.edit_text("\n".join(lines), disable_web_page_preview=True)


add_command_help("groupdata", [[".chatinfo [chat_id|username]", "Show title, ID, type, username and member count for a chat."]])
