import time
import traceback
from sys import version as pyver
import os
import shlex
import textwrap
from typing import Tuple
import asyncio 

from pyrogram import Client
from pyrogram import __version__ as pyrover
from pyrogram.enums import ParseMode
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
    Message,
)

from ICC import CMD_HELP, StartTime, app
from ICC.helper.data import Data
from config import OWNER_ID, REPO_URL
from ICC.helper.inline import inline_wrapper, paginate_help

async def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "Jam", "Hari"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += time_list.pop() + ", "

    time_list.reverse()
    up_time += ":".join(time_list)

    return up_time


async def alive_function(message: Message, answers):
    uptime = await get_readable_time((time.time() - StartTime))
    msg = f"""
<b>✦ 𝐈𝐂𝐂 𝐔sᴇʀʙᴏᴛ ✦</b>

<b>❏ 𝐕ᴇʀsɪᴏɴ:</b> <code>2.1</code>
<b>├• 𝐔ᴘᴛɪᴍᴇ:</b> <code>{uptime}</code>
<b>├• 𝐏ʏᴛʜᴏɴ:</b> <code>{pyver.split()[0]}</code>
<b>├• 𝐏ʏʀᴏɢʀᴀᴍ:</b> <code>{pyrover}</code>
<b>└• 𝐒ᴛᴀᴛᴜs:</b> <code>Online</code>
"""
    answers.append(
        InlineQueryResultArticle(
            title="Alive",
            description="Check Bot's Stats",
            thumb_url="https://telegra.ph/file/cc0890d0876bc18c19e05.jpg",
            input_message_content=InputTextMessageContent(
                msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("𝐇ᴇʟᴘ", callback_data="helper")],
                [
                    InlineKeyboardButton("𝐎ᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}") if OWNER_ID else InlineKeyboardButton("𝐎ᴡɴᴇʀ", url="https://t.me/GOVIND_USERBOT_UPDATE"),
                    InlineKeyboardButton("𝐑ᴇᴘᴏ", url=REPO_URL or "https://github.com/GOVIND-BOTS/Govinduserbot"),
                ],
                [
                    InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ 𝐆ʀᴏᴜᴘ", url="https://t.me/GOVIND_MP_USERBOT_SPPORT"),
                    InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇ 𝐂ʜᴀɴɴᴇʟ", url="https://t.me/GOVIND_USERBOT_UPDATE"),
                ],
            ]),
        )
    )
    return answers


async def help_function(answers):
    bttn = paginate_help(0, CMD_HELP, "helpme")
    bttn.append((
        InlineKeyboardButton("OWNER", url=f"tg://user?id={OWNER_ID}") if OWNER_ID else InlineKeyboardButton("OWNER", url="https://t.me/GOVIND_USERBOT_UPDATE"),
        InlineKeyboardButton("SUPPORT", url="https://t.me/GOVIND_MP_USERBOT_SPPORT"),
        InlineKeyboardButton("UPDATES", url="https://t.me/GOVIND_USERBOT_UPDATE"),
    ))
    answers.append(
        InlineQueryResultPhoto(
            photo_url="https://telegra.ph/file/cc0890d0876bc18c19e05.jpg",
            thumb_url="https://telegra.ph/file/cc0890d0876bc18c19e05.jpg",
            title="ICC Help Menu",
            description="Choose a module to view its commands",
            caption=(
                "<b>ICC USERBOT HELP MENU</b>\n"
                "<i>Select any module button below to see its commands.</i>\n\n"
                f"<b>Total Modules:</b> <code>{len(CMD_HELP)}</code>"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(bttn),
        )
    )
    return answers


@app.on_inline_query()
@inline_wrapper
async def inline_query_handler(client: Client, query):
    try:
        text = query.query.strip().lower()
        string_given = query.query.lower()
        answers = []
        if text.strip() == "":
            return
        elif text.split()[0] == "alive":
            answerss = await alive_function(query, answers)
            await client.answer_inline_query(query.id, results=answerss, cache_time=10)
        elif string_given.startswith("helper"):
            answers = await help_function(answers)
            await client.answer_inline_query(query.id, results=answers, cache_time=0)
    except Exception as e:
        e = traceback.format_exc()
        print(e, "InLine")
