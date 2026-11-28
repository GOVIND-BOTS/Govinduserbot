"""Per-chat blocked-word moderation for ICC Userbot.

Feature adapted for ICC Userbot from the source blacklist-words plugin.
"""
import os
import re
import sqlite3

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


DB_PATH = os.path.join(os.path.dirname(__file__), "blacklist.sqlite3")


def _run(query, params=(), fetch=False):
    connection = sqlite3.connect(DB_PATH)
    try:
        cursor = connection.execute(query, params)
        connection.commit()
        return cursor.fetchall() if fetch else cursor.rowcount
    finally:
        connection.close()


def _init():
    _run("CREATE TABLE IF NOT EXISTS blocked_words (chat_id INTEGER, word TEXT, PRIMARY KEY(chat_id, word))")


@Client.on_message(filters.command("addblacklist", ".") & filters.me)
async def add_words(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("Usage: `.addblacklist word1, word2`")
    _init()
    words = [word.strip().casefold() for word in message.text.split(maxsplit=1)[1].split(",") if word.strip()]
    for word in words:
        _run("INSERT OR IGNORE INTO blocked_words(chat_id, word) VALUES(?, ?)", (message.chat.id, word[:80]))
    await message.edit_text(f"Added `{len(words)}` blocked word(s) for this chat.")


@Client.on_message(filters.command("rmblacklist", ".") & filters.me)
async def remove_words(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("Usage: `.rmblacklist word1, word2`")
    _init()
    words = [word.strip().casefold() for word in message.text.split(maxsplit=1)[1].split(",") if word.strip()]
    removed = sum(_run("DELETE FROM blocked_words WHERE chat_id=? AND word=?", (message.chat.id, word)) for word in words)
    await message.edit_text(f"Removed `{removed}` blocked word(s).")


@Client.on_message(filters.command("listblacklist", ".") & filters.me)
async def list_words(client: Client, message: Message):
    _init()
    rows = _run("SELECT word FROM blocked_words WHERE chat_id=? ORDER BY word", (message.chat.id,), True)
    await message.edit_text("**Blocked words:**\n" + ("\n".join(f"• `{row[0]}`" for row in rows) if rows else "No blocked words saved."))


@Client.on_message(filters.group & filters.text & ~filters.me)
async def moderate_words(client: Client, message: Message):
    if not message.text or not message.from_user or message.from_user.is_bot:
        return
    _init()
    rows = _run("SELECT word FROM blocked_words WHERE chat_id=?", (message.chat.id,), True)
    text = message.text.casefold()
    if any(re.search(r"(?<!\w)" + re.escape(row[0]) + r"(?!\w)", text) for row in rows):
        try:
            await message.delete()
        except Exception:
            pass


add_command_help("blacklistwords", [
    [".addblacklist <words>", "Add comma-separated blocked words for the current chat."],
    [".rmblacklist <words>", "Remove blocked words from the current chat."],
    [".listblacklist", "List blocked words for the current chat."],
])
