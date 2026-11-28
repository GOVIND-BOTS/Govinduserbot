"""Timed mute and ban commands for group admins.

Feature adapted for ICC Userbot from the source timed-admin plugin.
"""
import re
from datetime import datetime, timedelta, timezone

from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatPermissions, Message

from ICC.modules.help import add_command_help


def _duration(value):
    match = re.fullmatch(r"(\d+)([smhd])", value.lower())
    if not match:
        return None
    amount = int(match.group(1))
    seconds = amount * {"s": 1, "m": 60, "h": 3600, "d": 86400}[match.group(2)]
    return seconds if 1 <= seconds <= 366 * 86400 else None


async def _check_admin(client, chat_id):
    member = await client.get_chat_member(chat_id, "me")
    return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)


@Client.on_message(filters.command(["tmute", "tban"], ".") & filters.me)
async def timed_admin(client: Client, message: Message):
    if not message.chat or message.chat.type.value not in ("group", "supergroup"):
        return await message.edit_text("Use this command in a group.")
    reply = message.reply_to_message
    if not reply or not reply.from_user:
        return await message.edit_text("Reply to a user: `.tmute 10m` or `.tban 2h`.")
    if len(message.command) < 2:
        return await message.edit_text("Provide duration: 30s, 10m, 2h or 1d.")
    seconds = _duration(message.command[1])
    if not seconds:
        return await message.edit_text("Invalid duration. Use 30s, 10m, 2h or 1d.")
    try:
        if not await _check_admin(client, message.chat.id):
            return await message.edit_text("Userbot must be a group admin.")
        until = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        if message.command[0].lower() == "tmute":
            await client.restrict_chat_member(
                message.chat.id, reply.from_user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until,
            )
            action = "muted"
        else:
            await client.ban_chat_member(message.chat.id, reply.from_user.id, until_date=until)
            action = "banned"
        await message.edit_text(f"{reply.from_user.mention} was {action} for `{message.command[1]}`.")
    except Exception as exc:
        await message.edit_text(f"Action failed: `{str(exc)[:250]}`")


add_command_help("tadmin", [
    [".tmute <duration> (reply)", "Temporarily mute a replied user (e.g. 10m, 2h)."],
    [".tban <duration> (reply)", "Temporarily ban a replied user (e.g. 1h, 1d)."],
])
