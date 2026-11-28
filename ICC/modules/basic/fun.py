import asyncio

from pyrogram import Client, filters
from ICC.modules.help import add_command_help

GA_FRAMES = [
    "अरे ओ आतिशबाज़ी 😄",
    "ज़रा कान खोलकर सुनना...",
    "बाप के सामने इतनी शरारत? 😂",
    "और तेरा बाप कौन है, पता है?",
    "नहीं पता तो जान ले...",
    "तेरा बाप है...",
    "तेरा अपना Sensei 😎",
    "**SENSEI PAPA 😂**",
    "अब चल, यहाँ से मुस्कुराते हुए निकल! 😜",
]

GAA_FRAMES = [
    "जा जाकर अपनी माँ से पूछना 😄",
    "**WHO IS YOUR FATHER?**",
    "पता है वो क्या कहेंगी? 😂",
    "\"बेटा, ये भी कोई पूछने की बात है!\"",
    "तेरा Sensei ही तेरा Sensei है 😎",
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
    [".ga", "Play the funny Sensei Papa text animation."],
    [".gaa", "Play the funny father-question text animation."],
])
