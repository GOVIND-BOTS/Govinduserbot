"""HTML-safe text formatting commands for Telegram."""
from html import escape

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


FORMATS = {
    "bold": ("<b>", "</b>"),
    "italic": ("<i>", "</i>"),
    "underline": ("<u>", "</u>"),
    "strike": ("<s>", "</s>"),
    "code": ("<code>", "</code>"),
    "spoiler": ("<tg-spoiler>", "</tg-spoiler>"),
}


async def _format_message(message: Message, command: str):
    value = " ".join(message.command[1:]).strip()
    if not value and message.reply_to_message:
        replied = message.reply_to_message
        value = replied.text or replied.caption or ""
    if not value:
        return await message.edit_text(f"Give text or reply to a message: `.{command} text`")
    opening, closing = FORMATS[command]
    await message.edit_text(f"{opening}{escape(value)}{closing}")


for _command in FORMATS:
    async def _handler(client: Client, message: Message, command=_command):
        await _format_message(message, command)
    _handler.__name__ = f"format_{_command}"
    Client.on_message(filters.command(_command, ".") & filters.me)(_handler)


@Client.on_message(filters.command("pre", ".") & filters.me)
async def format_pre(client: Client, message: Message):
    value = " ".join(message.command[1:]).strip()
    if not value and message.reply_to_message:
        value = message.reply_to_message.text or message.reply_to_message.caption or ""
    if not value:
        return await message.edit_text("Give text or reply to a message: `.pre text`")
    await message.edit_text(f"<pre>{escape(value)}</pre>")


add_command_help("markdown", [
    [".bold / .italic / .underline", "Format text using Telegram styles."],
    [".strike / .code / .pre", "Strike through text or show code."],
    [".spoiler", "Hide text behind a spoiler."],
])
