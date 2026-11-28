from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("resend", ".") & filters.me)
async def resend_message(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply:
        return await message.edit_text("Reply to a message with `.resend` to copy it without the forward header.")
    try:
        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=reply.chat.id,
            message_id=reply.id,
            reply_to_message_id=reply.id,
        )
        try:
            await message.delete()
        except Exception:
            pass
    except Exception as exc:
        await message.edit_text(f"**Resend error:** `{str(exc)[:350]}`")


add_command_help("resend", [
    [".resend", "Copy a replied message into the current chat without its forward attribution."],
])
