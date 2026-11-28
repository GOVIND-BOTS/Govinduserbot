from pyrogram import Client, enums, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from ICC import app, CMD_HELP, ids
from config import OWNER_ID
from ICC.helper.PyroHelpers import ReplyCheck


def _owner_button():
    return InlineKeyboardButton(
        "OWNER",
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
        InlineKeyboardButton("SUPPORT", url="https://t.me/GOVIND_BOTS"),
        InlineKeyboardButton("UPDATES", url="https://t.me/govindofficialmp"),
    ])
    rows.append([InlineKeyboardButton("CLOSE", callback_data="help_close")])
    return InlineKeyboardMarkup(rows)


def _help_menu_text():
    return (
        "✦ **ICC USERBOT HELP CENTER** ✦\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"**Available Modules:** `{len(CMD_HELP)}`\n"
        "Choose a module below to view its commands.\n"
        "Use `.help <module>` to open a module directly.\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "© **GOVIND-BOTS**"
    )


def _module_text(module):
    body = (
        f"✦ **ICC USERBOT | {module.upper()}** ✦\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
    )
    commands = CMD_HELP.get(module, {})
    if not commands:
        body += "No commands are registered for this module.\n"
    for command, description in commands.items():
        body += f"**✧ Command:** `{command}`\n"
        body += f"**✧ Description:** {description}\n\n"
    return body + "━━━━━━━━━━━━━━━━━━\n© **GOVIND-BOTS**"




def _normalize(value):
    return str(value).strip().lower().lstrip(".").replace("_", "").replace("-", "").replace(" ", "")


def _command_matches(label, query):
    label_text = str(label).lower().lstrip(".")
    candidates = [label_text.split()[0]]
    if " or " in label_text:
        candidates.extend(part.strip().split()[0] for part in label_text.split(" or "))
    wanted = _normalize(query)
    return any(_normalize(candidate) == wanted for candidate in candidates)


def _find_command(query):
    matches = []
    for module, commands in CMD_HELP.items():
        for command, description in commands.items():
            if _command_matches(command, query):
                matches.append((module, command, description))
    return matches


def _search_help(query, limit=15):
    needle = _normalize(query)
    results = []
    for module, commands in CMD_HELP.items():
        if needle in _normalize(module):
            results.append((module, None, None))
        for command, description in commands.items():
            if needle in _normalize(command) or needle in _normalize(description):
                results.append((module, command, description))
            if len(results) >= limit:
                return results
    return results[:limit]


def _command_text(module, command, description):
    return (
        f"✦ **ICC USERBOT | {module.upper()}** ✦\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"**Command:** {command}\n"
        f"**Description:** {description}\n\n"
        f"Use .help {module} to view all commands in this module.\n"
        "━━━━━━━━━━━━━━━━━━\n© **GOVIND-BOTS**"
    )


def _search_text(query, results):
    body = f"🔎 **HELP SEARCH: {query}**\n━━━━━━━━━━━━━━━━━━\n\n"
    if not results:
        return body + "No matching modules or commands found."
    for module, command, description in results:
        if command is None:
            body += f"**Module:** {module} — use .help {module}\n"
        else:
            body += f"**{module}** · {command}\n{description}\n\n"
    return body + "\nUse .help <module> to open the complete module help."


async def _send_help(client, message):
    assistant = await app.get_me()
    if not assistant.username:
        raise RuntimeError("Assistant bot must have a public username.")
    results = await client.get_inline_bot_results(assistant.username, "helper")
    if not results.results:
        raise RuntimeError("Assistant bot returned no Help Menu result.")
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
            await _send_help(client, message)
            await message.delete()
        except Exception as exc:
            await message.reply_text(
                f"Enable assistant bot Inline Mode in @BotFather using /setinline, then retry.\n\nError: {exc}"
            )
        return

    try:
        if help_arg.lower().startswith("search "):
            query = help_arg[7:].strip()
            if not query:
                return await message.reply_text("Usage: .help search <word>")
            text = _search_text(query, _search_help(query))
            sent = await _send_help(client, message)
            await _edit_help_message(sent, text, _detail_keyboard())
            await message.delete()
            return

        module = next((name for name in CMD_HELP if _normalize(name) == _normalize(help_arg)), None)
        if module:
            sent = await _send_help(client, message)
            await _edit_help_message(sent, _module_text(module), _detail_keyboard())
            await message.delete()
            return

        matches = _find_command(help_arg)
        if len(matches) == 1:
            module, command, description = matches[0]
            text = _command_text(module, command, description)
        elif matches:
            text = _search_text(help_arg, matches)
        else:
            results = _search_help(help_arg)
            if not results:
                return await message.reply_text(
                    f"{help_arg} was not found in Help.\n"
                    "Try .help for modules or .help search <word>."
                )
            text = _search_text(help_arg, results)

        sent = await _send_help(client, message)
        await _edit_help_message(sent, text, _detail_keyboard())
        await message.delete()
    except Exception as exc:
        await message.reply_text(
            f"Help menu error: {str(exc)[:250]}\n"
            "Check that assistant bot Inline Mode is enabled in @BotFather."
        )

@Client.on_message(filters.command(["plugins", "modules"], ".") & filters.me)
async def module_helper(client: Client, message: Message):
    return await module_help(client, message)


def _detail_keyboard():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("‹ BACK TO HELP", callback_data="help_open"),
        _owner_button(),
        InlineKeyboardButton("CLOSE", callback_data="help_close"),
    ]])

async def _edit_help_message(message, text, keyboard):
    if message.photo:
        return await message.edit_caption(
            caption=text,
            parse_mode=enums.ParseMode.MARKDOWN,
            reply_markup=keyboard,
        )
    return await message.edit_text(
        text=text,
        parse_mode=enums.ParseMode.MARKDOWN,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )


@app.on_callback_query(filters.regex(r"^help_(open|module|page):?|^help_close$"))
async def help_menu_callback(client, callback_query):
    user = callback_query.from_user
    allowed = set(ids)
    if OWNER_ID:
        allowed.add(OWNER_ID)
    if not user or (user.id not in allowed and not user.is_self):
        return await callback_query.answer(
            "This help menu is for the userbot owner.", show_alert=True
        )

    data = callback_query.data
    if data == "help_close":
        await callback_query.message.delete()
        return await callback_query.answer("Help menu closed.")

    if data == "help_open":
        await _edit_help_message(
            callback_query.message, _help_menu_text(), _help_keyboard(0)
        )
        return await callback_query.answer()

    if data.startswith("help_page:"):
        try:
            page = int(data.split(":", 1)[1])
        except ValueError:
            page = 0
        await _edit_help_message(
            callback_query.message, _help_menu_text(), _help_keyboard(page)
        )
        return await callback_query.answer()

    module = data.split(":", 1)[1]
    if module not in CMD_HELP:
        return await callback_query.answer("Module not found.", show_alert=True)

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("‹ BACK TO HELP", callback_data="help_open"),
        _owner_button(),
        InlineKeyboardButton("CLOSE", callback_data="help_close"),
    ]])
    await _edit_help_message(
        callback_query.message, _module_text(module), keyboard
    )
    await callback_query.answer()


def add_command_help(module_name, commands):
    command_dict = CMD_HELP.get(module_name, {})
    for item in commands:
        if len(item) >= 2:
            command_dict[item[0]] = item[1]
    CMD_HELP[module_name] = command_dict
