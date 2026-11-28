import traceback

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from ICC import CMD_HELP, app
from ICC.helper.data import Data
from ICC.helper.inline import cb_wrapper, paginate_help
from ICC import ids as users


def _new_help_keyboard(page=0):
    modules = sorted(CMD_HELP, key=str.lower)
    per_page = 16
    total = max(1, (len(modules) + per_page - 1) // per_page)
    page = max(0, min(page, total - 1))
    current = modules[page * per_page:(page + 1) * per_page]
    rows = []
    for index in range(0, len(current), 2):
        row = [InlineKeyboardButton(f"✦ {current[index].upper()}", callback_data=f"help_module:{current[index]}")]
        if index + 1 < len(current):
            row.append(InlineKeyboardButton(f"✦ {current[index + 1].upper()}", callback_data=f"help_module:{current[index + 1]}"))
        rows.append(row)
    nav = []
    if page:
        nav.append(InlineKeyboardButton("‹ PREVIOUS", callback_data=f"help_page:{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page + 1}/{total}", callback_data=f"help_page:{page}"))
    if page + 1 < total:
        nav.append(InlineKeyboardButton("NEXT ›", callback_data=f"help_page:{page + 1}"))
    rows.append(nav)
    rows.append([InlineKeyboardButton("CLOSE", callback_data="help_close")])
    return InlineKeyboardMarkup(rows)


def _new_help_caption():
    return (
        "<b>✦ ICC USERBOT — HELP MENU ✦</b>\\n\\n"
        f"<b>Available Modules:</b> <code>{len(CMD_HELP)}</code>\\n"
        "Select a module below to view its commands.\\n"
        "<i>POWERED BY GOVIND-BOTS</i>"
    )


def _new_module_caption(module):
    lines = [f"<b>✦ HELP: {module.upper()} ✦</b>", ""]
    for command, description in CMD_HELP.get(module, {}).items():
        lines.append(f"• <code>.{command}</code> — {description}")
    lines.extend(["", "<i>POWERED BY GOVIND-BOTS</i>"])
    return "\\n".join(lines)


async def _edit_help(callback_query, caption, keyboard):
    await app.edit_inline_caption(
        callback_query.inline_message_id,
        caption,
        reply_markup=keyboard,
    )


@Client.on_callback_query()
async def _callbacks(_, callback_query: CallbackQuery):
    data = callback_query.data or ""
    query = data.lower()

    # New help menu callbacks. Keep these in the catch-all handler because
    # Pyrogram stops dispatching after the first matching callback handler.
    if query.startswith("help_page:"):
        if callback_query.from_user.id not in users:
            return await callback_query.answer("This help menu is for connected users.", show_alert=True)
        try:
            page = int(query.split(":", 1)[1])
        except (ValueError, IndexError):
            page = 0
        await _edit_help(callback_query, _new_help_caption(), _new_help_keyboard(page))
        return await callback_query.answer()

    if query.startswith("help_module:"):
        if callback_query.from_user.id not in users:
            return await callback_query.answer("This help menu is for connected users.", show_alert=True)
        module = data.split(":", 1)[1]
        module = next((name for name in CMD_HELP if name.lower() == module.lower()), None)
        if not module:
            return await callback_query.answer("Module not found.", show_alert=True)
        back = InlineKeyboardMarkup([[
            InlineKeyboardButton("‹ BACK TO HELP", callback_data="help_page:0"),
            InlineKeyboardButton("CLOSE", callback_data="help_close"),
        ]])
        await _edit_help(callback_query, _new_module_caption(module), back)
        return await callback_query.answer()

    if query == "help_close":
        if callback_query.from_user.id not in users:
            return await callback_query.answer("This help menu is for connected users.", show_alert=True)
        await app.edit_inline_caption(callback_query.inline_message_id, "<b>ICC USERBOT — HELP MENU CLOSED</b>")
        return await callback_query.answer("Help menu closed.")

    # Legacy inline menu callbacks retained for older messages.
    bot_me = await app.get_me()
    if query == "helper":
        buttons = paginate_help(0, CMD_HELP, "helpme")
        await app.edit_inline_caption(
            callback_query.inline_message_id,
            Data.text_help_menu,
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return await callback_query.answer()
    elif query == "close":
        await app.edit_inline_caption(callback_query.inline_message_id, "**— CLOSED**")
        return await callback_query.answer()
    elif query == "close_help":
        if callback_query.from_user.id not in users:
            return await callback_query.answer("Not allowed.", show_alert=True)
        await app.edit_inline_caption(
            callback_query.inline_message_id,
            "**— CLOSED MENU HELP**",
            reply_markup=InlineKeyboardMarkup(Data.reopen),
        )
        return await callback_query.answer()
    elif query == "closed":
        try:
            await callback_query.message.delete()
        except Exception:
            pass
        try:
            await callback_query.message.reply_to_message.delete()
        except Exception:
            pass
        return await callback_query.answer()
    elif query == "make_basic_button":
        try:
            buttons = paginate_help(0, CMD_HELP, "helpme")
            await app.edit_inline_caption(
                callback_query.inline_message_id,
                Data.text_help_menu,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except Exception:
            print(traceback.format_exc(), "Callbacks")
        return await callback_query.answer()


@app.on_callback_query(filters.regex(r"^ub_modul_(.*)$"))
@cb_wrapper
async def on_plug_in_cb(_, callback_query: CallbackQuery):
    modul_name = callback_query.matches[0].group(1)
    commands: dict = CMD_HELP.get(modul_name, {})
    if not commands:
        return await callback_query.answer("Module not found.", show_alert=True)
    lines = [f"──「 **Help For {modul_name.upper()}** 」──", ""]
    for command, description in commands.items():
        lines.append(f"• **Command:** `.{command}`\\n• **Function:** `{description}`")
    await app.edit_inline_caption(
        callback_query.inline_message_id,
        "\\n\\n".join(lines),
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text="Return", callback_data="reopen"),
        ]]),
    )


@app.on_callback_query(filters.regex(r"^reopen$"))
@cb_wrapper
async def reopen_in_cb(_, callback_query: CallbackQuery):
    buttons = paginate_help(0, CMD_HELP, "helpme")
    await app.edit_inline_caption(
        callback_query.inline_message_id,
        Data.text_help_menu,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@app.on_callback_query(filters.regex(r"^helpme_prev\\((.+?)\\)$"))
@cb_wrapper
async def on_plug_prev_in_cb(_, callback_query: CallbackQuery):
    current_page_number = int(callback_query.matches[0].group(1))
    buttons = paginate_help(max(0, current_page_number - 1), CMD_HELP, "helpme")
    await app.edit_inline_caption(
        callback_query.inline_message_id,
        Data.text_help_menu,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


@app.on_callback_query(filters.regex(r"^helpme_next\\((.+?)\\)$"))
@cb_wrapper
async def on_plug_next_in_cb(_, callback_query: CallbackQuery):
    current_page_number = int(callback_query.matches[0].group(1))
    buttons = paginate_help(current_page_number + 1, CMD_HELP, "helpme")
    await app.edit_inline_caption(
        callback_query.inline_message_id,
        Data.text_help_menu,
        reply_markup=InlineKeyboardMarkup(buttons),
    )
