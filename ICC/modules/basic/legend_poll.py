"""Create Telegram polls using Pyrogram's native send_poll."""
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

@Client.on_message(filters.command("poll", ".") & filters.me)
async def create_poll(_, message):
    raw = message.text.split(maxsplit=1)
    if len(raw) < 2:
        return await message.edit("Usage: `.poll Question ; Option 1 ; Option 2 [; ...]`")
    parts = [part.strip() for part in raw[1].split(";") if part.strip()]
    if len(parts) < 3 or len(parts) > 11:
        return await message.edit("Give one question and 2–10 options separated by semicolons.")
    question, options = parts[0], parts[1:]
    if len(question) > 300 or any(len(option) > 100 for option in options):
        return await message.edit("Question limit: 300 characters; each option: 100 characters.")
    try:
        await message.reply_to_message.reply_poll(question, options) if message.reply_to_message else await message.reply_poll(question, options)
        await message.delete()
    except Exception as exc:
        await message.edit(f"Could not create poll: `{exc}`")

add_command_help("legend_poll", [[".poll Question ; Option 1 ; Option 2", "Create a Telegram poll with 2–10 options."]])
