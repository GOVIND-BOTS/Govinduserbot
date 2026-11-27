from datetime import datetime

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command(["stats", "status"], ".") & filters.me)
async def stats(client: Client, message: Message):
    status = await message.edit_text("Collecting stats...")
    start = datetime.now()
    users = groups = supergroups = channels = bots = admin_chats = 0
    me = await client.get_me()

    async for dialog in client.get_dialogs():
        chat = dialog.chat
        if chat.type == enums.ChatType.PRIVATE:
            users += 1
        elif chat.type == enums.ChatType.BOT:
            bots += 1
        elif chat.type == enums.ChatType.GROUP:
            groups += 1
        elif chat.type == enums.ChatType.SUPERGROUP:
            supergroups += 1
            try:
                member = await client.get_chat_member(chat.id, me.id)
                if member.status in (
                    enums.ChatMemberStatus.OWNER,
                    enums.ChatMemberStatus.ADMINISTRATOR,
                ):
                    admin_chats += 1
            except Exception:
                pass
        elif chat.type == enums.ChatType.CHANNEL:
            channels += 1

    elapsed = (datetime.now() - start).total_seconds()
    await status.edit_text(
        "Your account statistics\n\n"
        f"Private chats: {users}\n"
        f"Groups: {groups}\n"
        f"Supergroups: {supergroups}\n"
        f"Channels: {channels}\n"
        f"Admin in chats: {admin_chats}\n"
        f"Bots: {bots}\n"
        f"Completed in: {elapsed:.2f} seconds"
    )


add_command_help("stats", [["stats", "Check your account statistics."]])
