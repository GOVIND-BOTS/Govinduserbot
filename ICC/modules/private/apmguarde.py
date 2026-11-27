from pyrogram import filters, Client
import ICC.database.pmpermitdb as ICC
from ICC.modules.help import *
from .pmguard import get_arg

@Client.on_message(filters.command("pmguard", ["."]) & filters.me)
async def pmguard(client, message):
    arg = get_arg(message).lower()
    if arg not in ("on", "off"):
        return await message.edit("𝐔sᴀɢᴇ: .pmguard on / off")
    enabled = arg == "on"
    await ICC.set_pm(enabled)
    await message.edit(
        "𝐏𝐌 𝐆ᴜᴀʀᴅ 𝐀ᴄᴛɪᴠᴀᴛᴇᴅ." if enabled else "𝐏𝐌 𝐆ᴜᴀʀᴅ 𝐃ᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ."
    )


@Client.on_message(filters.command("setpmmsg", ["."]) & filters.me)
async def setpmmsg(client, message):
    arg = get_arg(message)
    if not arg:
        return await message.edit("𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴜsᴇ 'default'.")
    if arg.lower() == "default":
        await ICC.set_permit_message(ICC.PMPERMIT_MESSAGE)
        return await message.edit("𝐏𝐌 𝐆ᴜᴀʀᴅ ᴍᴇssᴀɢᴇ ʀᴇsᴇᴛ ᴛᴏ ᴅᴇғᴀᴜʟᴛ.")
    await ICC.set_permit_message(arg)
    await message.edit("𝐂ᴜsᴛᴏᴍ 𝐏𝐌 ᴍᴇssᴀɢᴇ sᴀᴠᴇᴅ.")


add_command_help(
    "antipm",
    [
        [".pmguard [on/off]", "Activates or deactivates PM Guard."],
        [".setpmmsg [message/default]", "Sets the PM Guard message."],
        [".setblockmsg [message/default]", "Sets the block message."],
        [".setlimit [value]", "Sets how many warnings are sent before blocking on the next DM."],
        [".allow", "Approves the current private chat."],
        [".deny", "Removes approval for the current private chat."],
    ],
)
