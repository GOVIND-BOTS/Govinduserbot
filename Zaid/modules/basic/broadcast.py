import asyncio

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from Zaid import SUDO_USER
from Zaid.modules.help import add_command_help
from cache.data import GROUP, VERIFIED_USERS

EXCLUDED_GROUPS = set(GROUP)
EXCLUDED_USERS = set(VERIFIED_USERS)


def get_arg(message: Message):
    if not message.text:
        return ""
    parts = message.text.split(None, 1)
    return parts[1].strip() if len(parts) > 1 else ""


async def _broadcast(client: Client, message: Message, private: bool = False):
    text = get_arg(message)
    source = message.reply_to_message
    if not source and not text:
        return await message.edit_text("Reply to a message or provide broadcast text.")

    progress = await message.reply_text("Starting global broadcast...")
    sent = 0
    failed = 0

    async for dialog in client.get_dialogs():
        chat = dialog.chat
        if private:
            eligible = (
                chat.type == enums.ChatType.PRIVATE
                and not chat.is_verified
                and chat.id not in EXCLUDED_USERS
            )
        else:
            eligible = (
                chat.type in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP)
                and chat.id not in EXCLUDED_GROUPS
            )

        if not eligible:
            continue

        try:
            if source:
                await source.copy(chat.id)
            else:
                await client.send_message(chat.id, text)
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.5)

    destination = "private chats" if private else "groups"
    await progress.edit_text(
        "Broadcast completed.\n"
        f"Successfully sent: {sent} {destination}\n"
        f"Failed: {failed}"
    )


@Client.on_message(
    filters.command("gcast", ".") & (filters.me | filters.user(SUDO_USER))
)
async def gcast_cmd(client: Client, message: Message):
    await _broadcast(client, message, private=False)


@Client.on_message(
    filters.command("gucast", ".") & (filters.me | filters.user(SUDO_USER))
)
async def gucast(client: Client, message: Message):
    await _broadcast(client, message, private=True)


add_command_help(
    "broadcast",
    [
        ["gcast [text/reply]", "Broadcast a message to groups."],
        ["gucast [text/reply]", "Broadcast a message to private chats."],
    ],
)
