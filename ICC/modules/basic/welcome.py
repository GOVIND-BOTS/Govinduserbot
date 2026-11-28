"""Configurable per-chat welcome messages for ICC Userbot.

Feature adapted for ICC Userbot from the source welcome plugin.
"""
import html
import os
import sqlite3

from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message

from ICC.modules.help import add_command_help


DB_PATH = os.path.join(os.path.dirname(__file__), "welcome.sqlite3")


def _db():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("CREATE TABLE IF NOT EXISTS welcome (chat_id INTEGER PRIMARY KEY, body TEXT NOT NULL)")
    return connection


@Client.on_message(filters.command("savewelcome", ".") & filters.me)
async def save_welcome(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text("Usage: `.savewelcome Welcome {mention} to {title}!`")
    body = message.text.split(maxsplit=1)[1]
    with _db() as connection:
        connection.execute("INSERT INTO welcome(chat_id, body) VALUES(?, ?) ON CONFLICT(chat_id) DO UPDATE SET body=excluded.body", (message.chat.id, body))
    await message.edit_text("Welcome message saved for this chat.")


@Client.on_message(filters.command("clearwelcome", ".") & filters.me)
async def clear_welcome(client: Client, message: Message):
    with _db() as connection:
        cursor = connection.execute("DELETE FROM welcome WHERE chat_id=?", (message.chat.id,))
    await message.edit_text("Welcome message cleared." if cursor.rowcount else "No welcome message was set.")


@Client.on_message(filters.new_chat_members)
async def welcome_new_members(client: Client, message: Message):
    with _db() as connection:
        row = connection.execute("SELECT body FROM welcome WHERE chat_id=?", (message.chat.id,)).fetchone()
    if not row:
        return
    title = html.escape(message.chat.title or "this chat")
    for user in message.new_chat_members:
        if user.is_bot:
            continue
        mention = f'<a href="tg://user?id={user.id}">{html.escape(user.first_name or "there")}</a>'
        body = row[0].replace("{mention}", mention)
        body = body.replace("{first}", html.escape(user.first_name or ""))
        body = body.replace("{username}", "@" + user.username if user.username else mention)
        body = body.replace("{userid}", str(user.id)).replace("{title}", title)
        try:
            await message.reply_text(body, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
        except Exception:
            await message.reply_text(f"Welcome {user.first_name or 'there'} to {message.chat.title or 'the group'}!")


add_command_help("welcome", [
    [".savewelcome <text>", "Set a welcome message. Placeholders: {mention}, {first}, {username}, {userid}, {title}."],
    [".clearwelcome", "Disable the welcome message for this chat."],
])
