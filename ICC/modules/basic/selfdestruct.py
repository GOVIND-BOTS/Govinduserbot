import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command(["sdm", "selfdm"], ".") & filters.me)
async def self_destruct_message(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.edit_text("Usage: `.sdm <seconds> <message>`")
    try:
        ttl = int(message.command[1])
        if not 3 <= ttl <= 86400:
            raise ValueError
    except ValueError:
        return await message.edit_text("Time must be between 3 seconds and 24 hours.")
    body = message.text.split(maxsplit=2)[2].strip()
    if not body:
        return await message.edit_text("Please provide the message text.")
    if len(body) > 4000:
        return await message.edit_text("Message is too long (maximum 4000 characters).")
    try:
        await message.delete()
    except Exception:
        pass
    sent = await client.send_message(
        message.chat.id,
        body + (f"\n\n_This message will self-destruct in {ttl} seconds._" if message.command[0].lower() == "selfdm" else ""),
        reply_to_message_id=message.reply_to_message.id if message.reply_to_message else None,
        disable_web_page_preview=True,
    )
    await asyncio.sleep(ttl)
    try:
        await sent.delete()
    except Exception:
        pass


add_command_help("selfdestruct", [
    [".sdm <seconds> <text>", "Send a message that deletes itself after 3 seconds–24 hours."],
    [".selfdm <seconds> <text>", "Same as .sdm, with a visible self-destruct timer."],
])
