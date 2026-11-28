"""Count the reply ancestry of a Telegram message."""
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

@Client.on_message(filters.command("chain", ".") & filters.me)
async def reply_chain(_, message):
    current = message.reply_to_message
    if not current:
        return await message.edit("Reply to a message with `.chain`.")
    chat_id = message.chat.id
    count = 0
    seen = set()
    status = await message.edit("Counting reply chain...")
    try:
        while current and current.id not in seen and count < 100:
            seen.add(current.id)
            count += 1
            reply_id = getattr(current, "reply_to_message_id", None)
            if not reply_id:
                break
            current = await message._client.get_messages(chat_id, reply_id)
        link = f"https://t.me/c/{str(chat_id)[4:]}/{message.reply_to_message.id}" if str(chat_id).startswith("-100") else ""
        suffix = f"\n[Open replied message]({link})" if link else ""
        await status.edit(f"**Reply chain length:** `{count}`{suffix}")
    except Exception as exc:
        await status.edit(f"Could not count reply chain: `{exc}`")

add_command_help("chain", [[".chain", "Count the reply ancestry of the replied message."]])
