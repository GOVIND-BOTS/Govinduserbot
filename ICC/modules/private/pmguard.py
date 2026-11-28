from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from ICC.database.pmpermitdb import get_approved_users, pm_guard
import ICC.database.pmpermitdb as ICC
from config import PM_LOGGER, ALIVE_PIC, OWNER_ID

USERS_AND_WARNS = {}
WAITING_USERS = set()


async def denied_users(_, client: Client, message: Message):
    if not await pm_guard():
        return False
    if message.chat.id in await get_approved_users():
        return False
    return True


def get_arg(message):
    msg = message.text or ""
    if len(msg) > 1 and msg[1] == " ":
        msg = msg.replace(" ", "", 1)
    split = msg[1:].replace("\n", " \n").split(" ")
    if " ".join(split[1:]).strip() == "":
        return ""
    return " ".join(split[1:])


def pm_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("𝐖ᴀɪᴛ ғᴏʀ ᴏᴡɴᴇʀ", callback_data="pmguard_wait")],
            [InlineKeyboardButton("𝐎ᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}") if OWNER_ID else InlineKeyboardButton("𝐎ᴡɴᴇʀ", url="https://t.me/GOVIND_USERBOT_UPDATE")],
            [
                InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url="https://t.me/GOVIND_MP_USERBOT_SPPORT"),
                InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url="https://t.me/GOVIND_USERBOT_UPDATE"),
            ],
        ]
    )


def warning_text(warn, limit):
    return (
        "𝐏ʀɪᴠᴀᴛᴇ 𝐌ᴇssᴀɢᴇ 𝐆ᴜᴀʀᴅ\n\n"
        "𝐓ʜɪs ᴀᴄᴄᴏᴜɴᴛ ɪs ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʙʏ 𝐈𝐂𝐂 𝐔sᴇʀʙᴏᴛ.\n"
        "𝐏ʟᴇᴀsᴇ ᴅᴏ ɴᴏᴛ sᴘᴀᴍ ᴏʀ sᴇɴᴅ ʀᴇᴘᴇᴀᴛᴇᴅ ᴍᴇssᴀɢᴇs.\n\n"
        f"𝐖ᴀʀɴɪɴɢ: {warn}/{limit}\n\n"
        "𝐏ʀᴇss ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴡᴀɪᴛ ғᴏʀ ᴛʜᴇ ᴏᴡɴᴇʀ."
    )


@Client.on_message(filters.command("setlimit", ["."]) & filters.me)
async def set_pm_limit(client, message):
    arg = get_arg(message)
    if not arg:
        return await message.edit("𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴡᴀʀɴɪɴɢ ʟɪᴍɪᴛ.")
    try:
        limit = int(arg)
        if limit < 1:
            raise ValueError
    except ValueError:
        return await message.edit("𝐋ɪᴍɪᴛ ᴍᴜsᴛ ʙᴇ ᴀ ᴘᴏsɪᴛɪᴠᴇ ɴᴜᴍʙᴇʀ.")
    await ICC.set_limit(limit)
    await message.edit(f"𝐏𝐌 𝐆ᴜᴀʀᴅ ʟɪᴍɪᴛ sᴇᴛ ᴛᴏ {limit} ᴡᴀʀɴɪɴɢs.")


@Client.on_message(filters.command("setblockmsg", ["."]) & filters.me)
async def set_pm_block_message(client, message):
    arg = get_arg(message)
    if not arg:
        return await message.edit("𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ʙʟᴏᴄᴋ ᴍᴇssᴀɢᴇ.")
    if arg.lower() == "default":
        await ICC.set_block_message(ICC.BLOCKED)
        return await message.edit("𝐁ʟᴏᴄᴋ ᴍᴇssᴀɢᴇ ʀᴇsᴇᴛ ᴛᴏ ᴅᴇғᴀᴜʟᴛ.")
    await ICC.set_block_message(arg)
    await message.edit("𝐂ᴜsᴛᴏᴍ ʙʟᴏᴄᴋ ᴍᴇssᴀɢᴇ sᴀᴠᴇᴅ.")


@Client.on_message(filters.command(["allow", "ap", "approve", "a"], ["."]) & filters.me & filters.private)
async def allow(client, message):
    chat_id = message.chat.id
    _, pm_message, _, _ = await ICC.get_pm_settings()
    await ICC.allow_user(chat_id)
    WAITING_USERS.discard(chat_id)
    USERS_AND_WARNS.pop(chat_id, None)
    await message.edit(f"𝐀ᴘᴘʀᴏᴠᴇᴅ [ᴛʜɪs ᴜsᴇʀ](tg://user?id={chat_id}) ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs.")
    async for old_message in client.search_messages(
        chat_id=chat_id, query=pm_message, limit=1, from_user="me"
    ):
        await old_message.delete()


@Client.on_message(filters.command(["deny", "dap", "disapprove", "dapp"], ["."]) & filters.me & filters.private)
async def deny(client, message):
    chat_id = message.chat.id
    await ICC.deny_user(chat_id)
    WAITING_USERS.discard(chat_id)
    USERS_AND_WARNS.pop(chat_id, None)
    await message.edit(f"𝐀ᴄᴄᴇss ʀᴇᴠᴏᴋᴇᴅ ғᴏʀ [ᴛʜɪs ᴜsᴇʀ](tg://user?id={chat_id}).")


@Client.on_callback_query(filters.regex("^pmguard_wait$"))
async def pmguard_wait_callback(client, callback_query):
    user_id = callback_query.from_user.id
    WAITING_USERS.add(user_id)
    await callback_query.answer("Your request has been noted.", show_alert=True)
    username = callback_query.from_user.username or "N/A"
    request_text = (
        f"𝐏𝐌 𝐆ᴜᴀʀᴅ ᴡᴀɪᴛ ʀᴇǫᴜᴇsᴛ\n\n"
        f"User ID: {user_id}\nUsername: @{username}"
    )
    for target in (OWNER_ID, PM_LOGGER):
        if target:
            try:
                await client.send_message(target, request_text, disable_web_page_preview=True)
            except Exception:
                pass
    await callback_query.message.reply_text(
        "𝐘ᴏᴜʀ ʀᴇǫᴜᴇsᴛ ʜᴀs ʙᴇᴇɴ ɴᴏᴛᴇᴅ.\n\n"
        "𝐏ʟᴇᴀsᴇ ᴡᴀɪᴛ ᴜɴᴛɪʟ ᴛʜᴇ ᴏᴡɴᴇʀ ᴄᴏᴍᴇs ᴏɴʟɪɴᴇ. "
        "𝐘ᴏᴜ ᴡɪʟʟ ɴᴏᴛ ʀᴇᴄᴇɪᴠᴇ ᴀɴʏ ᴍᴏʀᴇ ᴡᴀʀɴɪɴɢs ᴡʜɪʟᴇ ʏᴏᴜ ᴡᴀɪᴛ."
    )


@Client.on_message(
    filters.private
    & filters.create(denied_users)
    & filters.incoming
    & ~filters.service
    & ~filters.me
    & ~filters.bot
)
async def reply_pm(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in WAITING_USERS:
        return

    _, pm_message, limit, block_message = await ICC.get_pm_settings()
    warns = USERS_AND_WARNS.get(user_id, 0)

    if PM_LOGGER:
        try:
            await client.send_message(PM_LOGGER, f"𝐍ᴇᴡ ᴜɴᴀᴘᴘʀᴏᴠᴇᴅ 𝐏𝐌 ғʀᴏᴍ <code>{user_id}</code>.")
        except Exception:
            pass

    # Five warning messages are sent first; the next unwanted DM triggers a block.
    if warns >= limit:
        await message.reply_text(block_message, disable_web_page_preview=True)
        try:
            await client.block_user(user_id)
        finally:
            USERS_AND_WARNS.pop(user_id, None)
            WAITING_USERS.discard(user_id)
        return

    warns += 1
    USERS_AND_WARNS[user_id] = warns
    caption = warning_text(warns, limit)
    if pm_message != ICC.PMPERMIT_MESSAGE:
        caption = f"{pm_message}\n\n{caption}"
    keyboard = pm_keyboard()
    if ALIVE_PIC:
        try:
            await message.reply_photo(
                photo=ALIVE_PIC,
                caption=caption,
                reply_markup=keyboard,
            )
            return
        except Exception:
            pass
    await message.reply_text(caption, reply_markup=keyboard, disable_web_page_preview=True)
