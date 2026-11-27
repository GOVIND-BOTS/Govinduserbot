from random import randint
from typing import Optional

from pyrogram import Client, filters
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat
from pyrogram.types import Message

from ICC import SUDO_USER
from ICC.modules.help import add_command_help


def get_arg(message: Message):
    if not message.text:
        return ""
    parts = message.text.split(None, 1)
    return parts[1].strip() if len(parts) > 1 else ""


async def get_group_call(
    client: Client, message: Message, err_msg: str = ""
) -> Optional[InputGroupCall]:
    peer = await client.resolve_peer(message.chat.id)
    full_chat = None
    if isinstance(peer, InputPeerChannel):
        full_chat = (await client.invoke(GetFullChannel(channel=peer))).full_chat
    elif isinstance(peer, InputPeerChat):
        full_chat = (await client.invoke(GetFullChat(chat_id=peer.chat_id))).full_chat

    call = getattr(full_chat, "call", None)
    if call:
        return call
    await message.edit_text("No group call found. " + err_msg)
    return None


@Client.on_message(
    filters.command("startvc", ".") & (filters.me | filters.user(SUDO_USER))
)
async def opengc(client: Client, message: Message):
    title = get_arg(message)
    status = await message.reply_text("Processing...")
    try:
        peer = await client.resolve_peer(message.chat.id)
        params = {
            "peer": peer,
            "random_id": randint(10000, 999999999),
        }
        if title:
            params["title"] = title
        await client.invoke(CreateGroupCall(**params))
        result = "Group voice chat started."
        if title:
            result += "\nTitle: " + title
        await status.edit_text(result)
    except Exception as exc:
        await status.edit_text(
            "Could not start group call: " + type(exc).__name__
        )


@Client.on_message(
    filters.command("stopvc", ".") & (filters.me | filters.user(SUDO_USER))
)
async def end_vc_(client: Client, message: Message):
    call = await get_group_call(
        client, message, err_msg="The call may already have ended."
    )
    if not call:
        return
    try:
        await client.invoke(DiscardGroupCall(call=call))
        await message.reply_text(
            "Ended group call in chat " + str(message.chat.id)
        )
    except Exception as exc:
        await message.reply_text(
            "Could not end group call: " + type(exc).__name__
        )


add_command_help(
    "vctools",
    [
        ["startvc [title]", "Start a group voice chat."],
        ["stopvc", "End the current group voice chat."],
    ],
)
