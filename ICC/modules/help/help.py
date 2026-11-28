from pyrogram import Client, enums, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from ICC import app, CMD_HELP, ids
from config import OWNER_ID
from ICC.helper.PyroHelpers import ReplyCheck


def _owner_button():
    return InlineKeyboardButton(
        "𝐎ᴡɴᴇʀ",
        url=f"tg://user?id={OWNER_ID}" if OWNER_ID else "https://t.me/govindofficialmp",
    )


def _help_keyboard(page=0):
    modules = sorted(CMD_HELP, key=str.lower)
    per_page = 16
    total_pages = max(1, (len(modules) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    current = modules[page * per_page:(page + 1) * per_page]
    rows = []
    for index in range(0, len(current), 2):
        left = current[index]
        row = [InlineKeyboardButton(f"✦ {left.upper()}", callback_data=f"help_module:{left}")]
        if index + 1 < len(current):
            right = current[index + 1]
            row.append(InlineKeyboardButton(f"✦ {right.upper()}", callback_data=f"help_module:{right}"))
        rows.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("‹ PREVIOUS", callback_data=f"help_page:{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data=f"help_page:{page}"))
    if page + 1 < total_pages:
        nav.append(InlineKeyboardButton("NEXT ›", callback_data=f"help_page:{page+1}"))
    rows.append(nav)
    rows.append([
        _owner_button(),
        InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url="https://t.me/GOVIND_BOTS"),
        InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url="https://t.me/govindofficialmp"),
    ])
    rows.append([InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="help_close")])
    return InlineKeyboardMarkup(rows)


def _help_menu_text():
    return (
        "✦ **𝐈𝐂𝐂 𝐔sᴇʀʙᴏᴛ 𝐇ᴇʟᴘ 𝐌ᴇɴᴜ** ✦\n\n"
        f"**Available Modules:** `{len(CMD_HELP)}`\n"
        "Choose a plugin from the buttons below to view its commands."
    )


def _module_text(module):
    body = f"──「 **𝐇ᴇʟᴘ ғᴏʀ {module.upper()}** 」──\n\n"
    for command, description in CMD_HELP.get(module, {}).items():
        body += f"• **Command:** `{command}`\n• **Function:** `{description}`\n\n"
    return body + "© @GOVIND_MP_USERBOT_SPPORT"


async def _send_help(client, message, text, keyboard):
    assistant = await app.get_me()
    if not assistant.username:
        raise RuntimeError('Assistant bot must have a public username.')
    results = await client.get_inline_bot_results(assistant.username, 'helper')
    if not results.results:
        raise RuntimeError('Assistant bot returned no Help Menu result.')
    return await client.send_inline_bot_result(
        chat_id=message.chat.id,
        query_id=results.query_id,
        result_id=results.results[0].id,
        reply_to_message_id=ReplyCheck(message),
    )

@Client.on_message(filters.command(["help", "helpme"], ".") & filters.me)
async def module_help(client: Client, message: Message):
    help_arg = " ".join(message.command[1:]).strip() if len(message.command) > 1 else ""
    if not help_arg:
        try:
            await _send_help(client, message, _help_menu_text(), _help_keyboard(0))
            await message.delete()
        except Exception as exc:
            await message.reply_text(
                f"Enable assistant bot Inline Mode in @BotFather using /setinline, then retry.\n\nError: `{exc}`"
            )
        return

    module = next((name for name in CMD_HELP if name.lower() == help_arg.lower()), None)
    if not module:
        return await message.reply_text(f"`{help_arg}` **𝐍ᴏᴛ ᴀ 𝐕ᴀʟɪᴅ 𝐌ᴏᴅᴜʟᴇ 𝐍ᴀᴍᴇ.**")
    try:
        await _send_help(client, message, _module_text(module), InlineKeyboardMarkup([[
            InlineKeyboardButton("‹ BACK TO HELP", callback_data="help_page:0"),
            _owner_button(),
            InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="help_close"),
        ]]))
        await message.delete()
    except Exception as exc:
        await message.reply_text(f"Enable assistant bot Inline Mode in @BotFather using /setinline, then retry.\n\nError: `{exc}`")


@Client.on_message(filters.command(["plugins", "modules"], ".") & filters.me)
async def module_helper(client: Client, message: Message):
    return await module_help(client, message)


@app.on_callback_query(filters.regex(r"^help_(module|page):|^help_close$"))
async def help_menu_callback(client, callback_query):
    user = callback_query.from_user
    allowed = set(ids)
    if OWNER_ID:
        allowed.add(OWNER_ID)
    if not user or (user.id not in allowed and not user.is_self):
        return await callback_query.answer("This help menu is for the userbot owner.", show_alert=True)

    data = callback_query.data
    if data == "help_close":
        await callback_query.message.delete()
        return await callback_query.answer("Help menu closed.")

    if data.startswith("help_page:"):
        try:
            page = int(data.split(":", 1)[1])
        except ValueError:
            page = 0
        await callback_query.message.edit_caption(
            caption=_help_menu_text(),
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=_help_keyboard(page),
        )
        return await callback_query.answer()

    module = data.split(":", 1)[1]
    if module not in CMD_HELP:
        return await callback_query.answer("Module not found.", show_alert=True)

    await callback_query.message.edit_caption(
        caption=_module_text(module),
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("‹ BACK TO HELP", callback_data="help_page:0"),
            _owner_button(),
            InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="help_close"),
        ]]),
    )
    await callback_query.answer()


def add_command_help(module_name, commands):
    command_dict = CMD_HELP.get(module_name, {})
    for item in commands:
        if len(item) >= 2:
            command_dict[item[0]] = item[1]
    CMD_HELP[module_name] = command_dict
