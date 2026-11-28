# Original plugin by Govind for old HellBot.
# Pyrogram port for ICC Userbot; original author credit retained.
import asyncio

from pyrogram import Client, filters
from ICC.modules.help import add_command_help

# The original plugin cycles through these heart colours.
_LOVE_COLORS = (
    "❤", "🧡", "💛", "💚", "💙", "💜", "🤎",
    "💕", "💞", "💓", "💗", "💖", "💘", "💝", "♥",
)
_LOVE_FRAMES = [f"{color}😘" * 36 for color in _LOVE_COLORS]

@Client.on_message(filters.command("lslove", ".") & filters.me)
async def love_animation(_, message):
    try:
        for frame in _LOVE_FRAMES:
            await message.edit(frame)
            await asyncio.sleep(1)
    except Exception:
        # Stop cleanly if the message is deleted or Telegram rejects an edit.
        return

@Client.on_message(filters.command("hi", ".") & filters.me)
async def say_hi(_, message):
    await message.edit("☻/  Hello! 🌷\n/▌\n/ \\ ")

add_command_help("greetings", [[".lslove", "Play the colourful heart animation."], [".hi", "Send a simple greeting."]])
