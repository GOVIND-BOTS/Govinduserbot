import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("del", ".") & filters.me)
async def del_msg(client: Client, message: Message):
    if message.reply_to_message:
        try:
            await client.delete_messages(
                message.chat.id,
                message.reply_to_message.id,
            )
        except Exception:
            pass
    try:
        await message.delete()
    except Exception:
        pass


@Client.on_message(filters.command("purge", ".") & filters.me)
async def purge(client: Client, message: Message):
    source = message.reply_to_message
    if not source:
        return await message.edit_text("Reply to a message to purge from that point.")

    status = await message.edit_text("Starting purge...")
    deleted = 0
    for message_id in range(source.id, message.id):
        try:
            await client.delete_messages(
                chat_id=message.chat.id,
                message_ids=message_id,
                revoke=True,
            )
            deleted += 1
        except FloodWait as exc:
            await asyncio.sleep(exc.value)
        except Exception:
            continue

    try:
        await status.edit_text("Purge completed. Deleted " + str(deleted) + " messages.")
        await asyncio.sleep(2)
        await status.delete()
    except Exception:
        pass


@Client.on_message(filters.command("purgeme", ".") & filters.me)
async def purgeme(client: Client, message: Message):
    if len(message.command) != 2:
        return await message.edit_text("Usage: .purgeme COUNT")
    try:
        count = int(message.command[1])
    except ValueError:
        return await message.edit_text("Please enter a valid number.")
    if count < 1:
        return await message.edit_text("Count must be greater than zero.")

    message_ids = []
    async for item in client.get_chat_history(message.chat.id, limit=1000):
        if item.from_user and item.from_user.is_self:
            message_ids.append(item.id)
            if len(message_ids) >= min(count, 1000):
                break

    if not message_ids:
        return await message.edit_text("No outgoing messages found.")

    for offset in range(0, len(message_ids), 100):
        await client.delete_messages(
            chat_id=message.chat.id,
            message_ids=message_ids[offset:offset + 100],
            revoke=True,
        )


add_command_help(
    "purge",
    [
        ["del", "Delete the replied-to message."],
        ["purge", "Delete messages from the replied-to message onward."],
        ["purgeme [count]", "Delete your recent outgoing messages."],
    ],
)
