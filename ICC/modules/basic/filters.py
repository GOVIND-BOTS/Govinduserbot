"""Per-chat keyword auto-replies for ICC Userbot.

Feature adapted for ICC Userbot from the source filters plugin.
"""
import os
import sqlite3

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


DB_PATH = os.path.join(os.path.dirname(__file__), "filters.sqlite3")


def _run(query, params=(), fetch=False):
    connection = sqlite3.connect(DB_PATH)
    try:
        cursor = connection.execute(query, params)
        connection.commit()
        return cursor.fetchall() if fetch else cursor.rowcount
    finally:
        connection.close()


@Client.on_message(filters.command("filter", ".") & filters.me)
async def add_filter(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("Usage: `.filter keyword ; reply text`")
    raw = message.text.split(maxsplit=1)[1]
    if ";" not in raw:
        return await message.edit_text("Separate the keyword and reply with a semicolon.")
    keyword, response = [part.strip() for part in raw.split(";", 1)]
    if not keyword or not response or len(keyword) > 80:
        return await message.edit_text("Keyword or reply is empty/too long.")
    _run(
        "CREATE TABLE IF NOT EXISTS chat_filters (chat_id INTEGER, keyword TEXT, response TEXT, PRIMARY KEY(chat_id, keyword))"
    )
    _run(
        "INSERT INTO chat_filters VALUES(?, ?, ?) ON CONFLICT(chat_id, keyword) DO UPDATE SET response=excluded.response",
        (message.chat.id, keyword.casefold(), response),
    )
    await message.edit_text(f"Saved filter for `{keyword}` in this chat.")


@Client.on_message(filters.command("filters", ".") & filters.me)
async def list_filters(client: Client, message: Message):
    _run("CREATE TABLE IF NOT EXISTS chat_filters (chat_id INTEGER, keyword TEXT, response TEXT, PRIMARY KEY(chat_id, keyword))")
    rows = _run("SELECT keyword FROM chat_filters WHERE chat_id=? ORDER BY keyword", (message.chat.id,), True)
    await message.edit_text("**Chat filters:**\n" + ("\n".join(f"• `{row[0]}`" for row in rows) if rows else "No filters saved."))


@Client.on_message(filters.command("stop", ".") & filters.me)
async def remove_filter(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("Usage: `.stop keyword`")
    _run("CREATE TABLE IF NOT EXISTS chat_filters (chat_id INTEGER, keyword TEXT, response TEXT, PRIMARY KEY(chat_id, keyword))")
    count = _run("DELETE FROM chat_filters WHERE chat_id=? AND keyword=?", (message.chat.id, message.text.split(maxsplit=1)[1].casefold()))
    await message.edit_text("Filter removed." if count else "Filter not found.")


@Client.on_message(filters.text & ~filters.me & ~filters.bot)
async def filter_incoming(client: Client, message: Message):
    if not message.text or message.text.startswith("."):
        return
    _run("CREATE TABLE IF NOT EXISTS chat_filters (chat_id INTEGER, keyword TEXT, response TEXT, PRIMARY KEY(chat_id, keyword))")
    rows = _run("SELECT keyword, response FROM chat_filters WHERE chat_id=?", (message.chat.id,), True)
    text = message.text.casefold()
    for keyword, response in rows:
        if text == keyword:
            await message.reply_text(response, disable_web_page_preview=True)
            break


add_command_help("filters", [
    [".filter <keyword> ; <reply>", "Save an exact-match auto-reply for the current chat."],
    [".filters", "List saved auto-replies in the current chat."],
    [".stop <keyword>", "Remove an auto-reply from the current chat."],
])
