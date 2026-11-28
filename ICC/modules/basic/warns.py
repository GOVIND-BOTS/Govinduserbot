"""Per-chat warning counter for ICC Userbot.

Feature adapted for ICC Userbot from the source warns plugin.
Warnings are tracked only; no automatic ban or kick is performed.
"""
import os
import sqlite3

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


DB_PATH = os.path.join(os.path.dirname(__file__), "warns.sqlite3")


def _run(query, params=(), fetch=False):
    connection = sqlite3.connect(DB_PATH)
    try:
        cursor = connection.execute(query, params)
        connection.commit()
        return cursor.fetchall() if fetch else cursor.rowcount
    finally:
        connection.close()


def _init():
    _run("CREATE TABLE IF NOT EXISTS warnings (chat_id INTEGER, user_id INTEGER, reason TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")


@Client.on_message(filters.command("warn", ".") & filters.me)
async def warn_user(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.from_user:
        return await message.edit_text("Reply to a user with `.warn [reason]`.")
    if reply.from_user.is_bot:
        return await message.edit_text("Bots cannot be warned.")
    _init()
    reason = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else "No reason"
    _run("INSERT INTO warnings(chat_id, user_id, reason) VALUES(?, ?, ?)", (message.chat.id, reply.from_user.id, reason[:300]))
    rows = _run("SELECT COUNT(*) FROM warnings WHERE chat_id=? AND user_id=?", (message.chat.id, reply.from_user.id), True)
    await message.edit_text(f"Warned {reply.from_user.mention}.\nWarnings: `{rows[0][0]}`\nReason: {reason[:300]}")


@Client.on_message(filters.command("warns", ".") & filters.me)
async def list_warnings(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.from_user:
        return await message.edit_text("Reply to a user with `.warns`.")
    _init()
    rows = _run("SELECT reason, created_at FROM warnings WHERE chat_id=? AND user_id=? ORDER BY rowid DESC LIMIT 20", (message.chat.id, reply.from_user.id), True)
    if not rows:
        return await message.edit_text("This user has no warnings in this chat.")
    body = "\n".join(f"• {reason} — {created}" for reason, created in rows)
    await message.edit_text(f"**Warnings for {reply.from_user.mention}:**\n{body}")


@Client.on_message(filters.command("resetwarns", ".") & filters.me)
async def reset_warnings(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.from_user:
        return await message.edit_text("Reply to a user with `.resetwarns`.")
    _init()
    count = _run("DELETE FROM warnings WHERE chat_id=? AND user_id=?", (message.chat.id, reply.from_user.id))
    await message.edit_text(f"Removed `{count}` warning(s) for {reply.from_user.mention}.")


add_command_help("warns", [
    [".warn [reason] (reply)", "Add a warning to a user in this chat."],
    [".warns (reply)", "List the latest warnings for a user."],
    [".resetwarns (reply)", "Clear a user's warnings in this chat."],
])
