import time
import traceback
from sys import version as pyver

from pyrogram import Client
from pyrogram import __version__ as pyrover
from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultPhoto,
)

from ICC import CMD_HELP, StartTime
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
        [InlineKeyboardButton("𝐇ᴇʟᴘ", switch_inline_query_current_chat="helper")],
        [
            InlineKeyboardButton("𝐎ᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}" if OWNER_ID else "https://t.me/govindofficialmp"),
            InlineKeyboardButton("𝐑ᴇᴘᴏ", url=REPO_URL or "https://github.com/GOVIND-BOTS/Govinduserbot"),
        ],
        [
            InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ 𝐆ʀᴏᴜᴘ", url="https://t.me/GOVIND_BOTS"),
            InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇ 𝐂ʜᴀɴɴᴇʟ", url="https://t.me/govindofficialmp"),
        ],
    ])


async def alive_function(message, answers):
    uptime = await get_readable_time(time.time() - StartTime)
    caption = (
        "<b>✦ ICC USERBOT ✦</b>\\n\\n"
        "<b>❏ Version:</b> <code>2.1</code>\\n"
        f"<b>├• Uptime:</b> <code>{uptime}</code>\\n"
        f"<b>├• Python:</b> <code>{pyver.split()[0]}</code>\\n"
        f"<b>├• Pyrogram:</b> <code>{pyrover}</code>\\n"
        "<b>└• Status:</b> <code>Online</code>\\n\\n"
        "<i>POWERED BY GOVIND-BOTS</i>"
    )
    photo = ALIVE_PIC.strip() if ALIVE_PIC else ""
    if not photo:
        raise RuntimeError("Set ALIVE_PIC to the ICC USERBOT logo image URL in your hosting environment.")
    answers.append(
        InlineQueryResultPhoto(
            photo_url=photo,
            thumb_url=photo,
            title="ICC USERBOT Alive",
            description="ICC USERBOT status and uptime",
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=_alive_keyboard(),
        )
    )
    return answers


async def help_function(answers):
    photo = ALIVE_PIC.strip() if ALIVE_PIC else ""
    if not photo:
        raise RuntimeError("Set ALIVE_PIC to the ICC USERBOT logo image URL in your hosting environment.")
    from ICC.modules.help.help import _help_keyboard

    answers.append(
        InlineQueryResultPhoto(
            photo_url=photo,
            thumb_url=photo,
            title="ICC USERBOT Help Menu",
            description="Choose a module to view its commands",
            caption=(
                f"<b>✦ ICC USERBOT HELP MENU ✦</b>\\n\\n"
                f"<b>Available Modules:</b> <code>{len(CMD_HELP)}</code>\\n"
                "Choose a module below.\\n"
                "<i>POWERED BY GOVIND-BOTS</i>"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=_help_keyboard(0),
        )
    )
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
