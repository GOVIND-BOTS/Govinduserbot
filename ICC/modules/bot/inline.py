import time
import traceback
from html import escape
from sys import version as pyver

from pyrogram import Client
from pyrogram import __version__ as pyrover
from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from ICC import CMD_HELP, StartTime, app
from config import OWNER_ID, REPO_URL, ALIVE_PIC
from ICC.helper.inline import inline_wrapper


async def get_readable_time(seconds: int) -> str:
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


def _alive_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✦ HELP MENU ✦", callback_data="help_open")],
        [
            InlineKeyboardButton(
                "OWNER",
                url=f"tg://user?id={OWNER_ID}" if OWNER_ID else "https://t.me/govindofficialmp",
            ),
            InlineKeyboardButton(
                "SOURCE CODE",
                url=REPO_URL or "https://github.com/GOVIND-BOTS/Govinduserbot",
            ),
        ],
        [
            InlineKeyboardButton("SUPPORT GROUP", url="https://t.me/GOVIND_BOTS"),
            InlineKeyboardButton("UPDATES", url="https://t.me/govindofficialmp"),
        ],
    ])


async def alive_function(query, answers):
    uptime = await get_readable_time(time.time() - StartTime)
    owner = query.from_user
    owner_name = escape(owner.first_name or "User")
    caption = (
        "<b>✦ ICC USERBOT IS ONLINE ✦</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"<b>✧ Master:</b> <a href=\"tg://user?id={owner.id}\">{owner_name}</a>\n"
        f"<b>✧ Uptime:</b> <code>{uptime}</code>\n"
        f"<b>✧ Python:</b> <code>{escape(pyver.split()[0])}</code>\n"
        f"<b>✧ Pyrogram:</b> <code>{escape(pyrover)}</code>\n"
        "<b>✧ Status:</b> <code>All systems operational</code>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<i>POWERED BY GOVIND-BOTS</i>"
    )
    photo = ALIVE_PIC.strip() if ALIVE_PIC else ""
    if photo:
        answers.append(InlineQueryResultPhoto(
            photo_url=photo,
            thumb_url=photo,
            title="ICC USERBOT Alive",
            description="Live status, owner and uptime",
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=_alive_keyboard(),
        ))
    else:
        answers.append(InlineQueryResultArticle(
            title="ICC USERBOT Alive",
            description="Live status, owner and uptime",
            input_message_content=InputTextMessageContent(
                caption, parse_mode=ParseMode.HTML
            ),
            reply_markup=_alive_keyboard(),
        ))
    return answers


async def help_function(answers):
    photo = ALIVE_PIC.strip() if ALIVE_PIC else ""
    from ICC.modules.help.help import _help_keyboard

    caption = (
        "<b>✦ ICC USERBOT HELP CENTER ✦</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"<b>Available modules:</b> <code>{len(CMD_HELP)}</code>\n"
        "<i>Select a module below to view its commands and descriptions.</i>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "<i>POWERED BY GOVIND-BOTS</i>"
    )
    keyboard = _help_keyboard(0)
    if photo:
        answers.append(InlineQueryResultPhoto(
            photo_url=photo,
            thumb_url=photo,
            title="ICC USERBOT Help Menu",
            description="Browse modules and commands",
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
        ))
    else:
        answers.append(InlineQueryResultArticle(
            title="ICC USERBOT Help Menu",
            description="Browse modules and commands",
            input_message_content=InputTextMessageContent(
                caption, parse_mode=ParseMode.HTML
            ),
            reply_markup=keyboard,
        ))
    return answers


@app.on_inline_query()
@inline_wrapper
async def inline_query_handler(client: Client, query):
    try:
        text = query.query.strip().lower()
        if not text:
            return
        answers = []
        if text.split()[0] == "alive":
            results = await alive_function(query, answers)
            await client.answer_inline_query(query.id, results=results, cache_time=10)
        elif text.startswith("helper"):
            results = await help_function(answers)
            await client.answer_inline_query(query.id, results=results, cache_time=0)
    except Exception:
        print(traceback.format_exc(), "InLine")
