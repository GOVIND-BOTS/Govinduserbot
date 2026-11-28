"""Per-chat text snippets for ICC Userbot.

ICC USERBOT snippet module.
"""
import os
import re
import sqlite3

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


DB_PATH = os.path.join(os.path.dirname(__file__), "snips.sqlite3")


def _db():
    connection = sqlite3.connect(DB_PATH)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS snippets (chat_id INTEGER NOT NULL, keyword TEXT NOT NULL, body TEXT NOT NULL, PRIMARY KEY(chat_id, keyword))"
    )
    return connection


@Client.on_message(filters.command("snips", ".") & filters.me)
async def save_snip(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.edit_text("Usage: `.snips <keyword> <text>`")
    keyword = message.command[1].lower().lstrip("#")
    body = message.text.split(maxsplit=2)[2].strip()
    if not re.fullmatch(r"[a-z0-9_]{1,32}", keyword):
        return await message.edit_text("Keyword may contain only letters, numbers and underscores.")
    with _db() as connection:
        connection.execute(
            "INSERT INTO snippets(chat_id, keyword, body) VALUES(?, ?, ?) ON CONFLICT(chat_id, keyword) DO UPDATE SET body=excluded.body",
            (message.chat.id, keyword, body),
        )
    await message.edit_text(f"Saved `#{keyword}` for this chat.")


@Client.on_message(filters.command("snipdel", ".") & filters.me)
async def delete_snip(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("Usage: `.snipdel <keyword>`")
    keyword = message.command[1].lower().lstrip("#")
    with _db() as connection:
        cursor = connection.execute("DELETE FROM snippets WHERE chat_id=? AND keyword=?", (message.chat.id, keyword))
    await message.edit_text("Snippet deleted." if cursor.rowcount else "Snippet not found.")


@Client.on_message(filters.command("snipl", ".") & filters.me)
async def list_snips(client: Client, message: Message):
    with _db() as connection:
        rows = connection.execute("SELECT keyword FROM snippets WHERE chat_id=? ORDER BY keyword", (message.chat.id,)).fetchall()
    await message.edit_text("**Saved snippets:**\n" + ("\n".join(f"• `#{row[0]}`" for row in rows) if rows else "No snippets saved in this chat."))


@Client.on_message(filters.regex(r"^#([a-zA-Z0-9_]{1,32})$") & ~filters.me)
async def send_snip(client: Client, message: Message):
    keyword = message.text[1:].lower()
    with _db() as connection:
        row = connection.execute("SELECT body FROM snippets WHERE chat_id=? AND keyword=?", (message.chat.id, keyword)).fetchone()
    if row:
        await message.reply_text(row[0], disable_web_page_preview=True)


add_command_help("snip", [
    [".snips <keyword> <text>", "Save or update a text snippet for the current chat."],
    [".snipl", "List saved snippets in the current chat."],
    [".snipdel <keyword>", "Delete a snippet from the current chat."],
    ["#keyword", "Send a saved snippet in the current chat."],
])
