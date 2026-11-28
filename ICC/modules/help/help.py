import asyncio

from pyrogram import Client, enums, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from ICC import app, CMD_HELP, ids
from ICC.helper.PyroHelpers import ReplyCheck


def _help_keyboard(page=0):
    modules = sorted(CMD_HELP)
    per_page = 16
    total_pages = max(1, (len(modules) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    current = modules[page * per_page:(page + 1) * per_page]
    rows = []
    for index in range(0, len(current), 2):
        left = current[index]
        row = [InlineKeyboardButton(left.upper(), callback_data=f"help_module:{left}")]
        if index + 1 < len(current):
            right = current[index + 1]
            row.append(InlineKeyboardButton(right.upper(), callback_data=f"help_module:{right}"))
        rows.append(row)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("‹ PREVIOUS", callback_data=f"help_page:{page-1}"))
    nav.append(InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="help_page:0"))
    if page + 1 < total_pages:
        nav.append(InlineKeyboardButton("NEXT ›", callback_data=f"help_page:{page+1}"))
    rows.append(nav)
    rows.append([
        InlineKeyboardButton("SUPPORT", url="https://t.me/GOVIND_MP_USERBOT_SPPORT"),
        InlineKeyboardButton("UPDATES", url="https://t.me/GOVIND_USERBOT_UPDATE"),
        InlineKeyboardButton("CLOSE", callback_data="help_close"),
    ])
    return InlineKeyboardMarkup(rows)


def _help_menu_text():
    return (
        "✦ **𝐈𝐂𝐂 𝐔sᴇʀʙᴏᴛ 𝐇ᴇʟᴘ 𝐌ᴇɴᴜ** ✦\n\n"
        "Select any plugin button below to view its commands and description.\n\n"
        f"**Available Modules:** `{len(CMD_HELP)}`"
    )


async def edit_or_reply(message: Message, *args, **kwargs) -> Message:
    target = message.edit_text if bool(message.from_user and message.from_user.is_self or message.outgoing) else (message.reply_to_message or message).reply_text
    return await target(*args, **kwargs)


async def _show_module(message, module):
    commands = CMD_HELP.get(module, {})
    body = f"──「 **𝐇ᴇʟᴘ ғᴏʀ {module.upper()}** 」──\n\n"
    for command, description in commands.items():
        body += f"• **Command:** `{command}`\n• **Function:** `{description}`\n\n"
    body += "© @GOVIND_MP_USERBOT_SPPORT"
    await edit_or_reply(
        message, body, parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("‹ BACK TO HELP", callback_data="help_page:0"),
            InlineKeyboardButton("CLOSE", callback_data="help_close"),
        ]]),
    )


@Client.on_message(filters.command(["help", "helpme"], ".") & filters.me)
async def module_help(client: Client, message: Message):
    help_arg = " ".join(message.command[1:]).strip() if len(message.command) > 1 else ""
    if not help_arg:
        return await edit_or_reply(message, _help_menu_text(), reply_markup=_help_keyboard(0))
    module = next((name for name in CMD_HELP if name.lower() == help_arg.lower()), None)
    if not module:
        return await edit_or_reply(message, f"`{help_arg}` **𝐍ᴏᴛ ᴀ 𝐕ᴀʟɪᴅ 𝐌ᴏᴅᴜʟᴇ 𝐍ᴀᴍᴇ.**")
    await _show_module(message, module)


@Client.on_message(filters.command(["plugins", "modules"], ".") & filters.me)
async def module_helper(client: Client, message: Message):
    help_arg = " ".join(message.command[1:]).strip() if len(message.command) > 1 else ""
    if not help_arg:
        return await edit_or_reply(message, _help_menu_text(), reply_markup=_help_keyboard(0))
    module = next((name for name in CMD_HELP if name.lower() == help_arg.lower()), None)
    if not module:
        return await edit_or_reply(message, f"`{help_arg}` **𝐍ᴏᴛ ᴀ 𝐕ᴀʟɪᴅ 𝐌ᴏᴅᴜʟᴇ 𝐍ᴀᴍᴇ.**")
    await _show_module(message, module)


@Client.on_callback_query(filters.regex(r"^help_(module|page):|^help_close$"))
async def help_menu_callback(client, callback_query):
    user = callback_query.from_user
    if not user or not (user.is_self or user.id in ids):
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
        await callback_query.message.edit_text(_help_menu_text(), reply_markup=_help_keyboard(page))
        return await callback_query.answer()
    module = data.split(":", 1)[1]
    if module not in CMD_HELP:
        return await callback_query.answer("Module not found.", show_alert=True)
    commands = CMD_HELP.get(module, {})
    body = f"──「 **𝐇ᴇʟᴘ ғᴏʀ {module.upper()}** 」──\n\n"
    for command, description in commands.items():
        body += f"• **Command:** `{command}`\n• **Function:** `{description}`\n\n"
    body += "© @GOVIND_MP_USERBOT_SPPORT"
    await callback_query.message.edit_text(
        body, parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("‹ BACK TO HELP", callback_data="help_page:0"),
            InlineKeyboardButton("CLOSE", callback_data="help_close"),
        ]]),
    )
    await callback_query.answer()


def add_command_help(module_name, commands):
    command_dict = CMD_HELP.get(module_name, {})
    for item in commands:
        if len(item) >= 2:
            command_dict[item[0]] = item[1]
    CMD_HELP[module_name] = command_dict
