import asyncio

from pyrogram import Client, filters
from ICC.modules.help import add_command_help

GA_FRAMES = [
    "Abey O aatishbaji lodu 😈",
    "Kaan khol ke sun le...",
    "Baap ke samne bakchodi nahi!",
    "Aur tera baap kaun hai, jaanta hai na?",
    "Nahi jaanta to jaan le...",
    "Main hoon tera baap!",
    "Naam hai Sensei...",
    "**SENSEI PAPA** 😎",
    "Ab nikal yahan se madarchod 😂",
]

GAA_FRAMES = [
    "Jaa jaakar apni maa se poochna...",
    "**WHO IS YOUR FATHER?**",
    "Pata hai teri maa kya bolegi?",
    "\"Lode beta, ye koi poochhne ki baat hai?\"",
    "Tera baap Sensei hai aur wahi rahega! 😂",
]

async def _play_frames(message, frames, delay=0.9):
    for frame in frames:
        await message.edit(frame)
        await asyncio.sleep(delay)

@Client.on_message(filters.command("ga", ".") & filters.me)
async def ga_fun(_, message):
    try:
        await _play_frames(message, GA_FRAMES)
    except Exception:
        return

@Client.on_message(filters.command("gaa", ".") & filters.me)
async def gaa_fun(_, message):
    try:
        await _play_frames(message, GAA_FRAMES)
    except Exception:
        return

add_command_help("fun", [
    [".ga", "Play the funny gaali wali Sensei Papa animation."],
    [".gaa", "Play the funny gaali wali father-question animation."],
])
