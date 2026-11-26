import asyncio
from time import time

from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message

from Zaid.helper.interval import IntervalHelper


async def CheckAdmin(message: Message):
    if not message.from_user:
        return False
    member = await message._client.get_chat_member(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
    )
    if member.status == ChatMemberStatus.OWNER:
        return True
    privileges = member.privileges
    if member.status == ChatMemberStatus.ADMINISTRATOR and privileges:
        if privileges.can_restrict_members:
            return True
    try:
        await message.edit("You need administrator permissions to use this command.")
        await asyncio.sleep(2)
        await message.delete()
    except Exception:
        pass
    return False


async def CheckReplyAdmin(message: Message):
    reply = message.reply_to_message
    if not reply:
        await message.edit("The command needs to be a reply.")
        await asyncio.sleep(2)
        await message.delete()
        return False
    if not reply.from_user or reply.from_user.is_self:
        await message.edit("I cannot perform this action on that sender.")
        await asyncio.sleep(2)
        await message.delete()
        return False
    return True


async def Timer(message: Message):
    if len(message.command) > 1:
        interval = IntervalHelper(message.command[1])
        return int(time() + interval.to_secs()[0])
    return 0


async def TimerString(message: Message):
    if len(message.command) < 2:
        return ""
    interval = IntervalHelper(message.command[1])
    return f"{interval.to_secs()[1]} {interval.to_secs()[2]}"


async def RestrictFailed(message: Message):
    command = message.command[0] if message.command else "this action"
    await message.edit(f"I can't {command} this user.")
    await asyncio.sleep(2)
    await message.delete()
