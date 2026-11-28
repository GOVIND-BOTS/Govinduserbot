import asyncio
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

FRAMES = [
    "❤😘❤😘❤😘❤😘❤😘❤😘❤😘",
    "🧡😘🧡😘🧡😘🧡😘🧡😘🧡😘",
    "💛😘💛😘💛😘💛😘💛😘💛😘",
    "💚😘💚😘💚😘💚😘💚😘💚😘",
    "💙😘💙😘💙😘💙😘💙😘💙😘",
]

@Client.on_message(filters.command("lslove", ".") & filters.me)
async def love_animation(_, message):
    try:
        for frame in FRAMES:
            await message.edit(frame)
            await asyncio.sleep(1)
    except Exception:
        pass

@Client.on_message(filters.command("hi", ".") & filters.me)
async def say_hi(_, message):
    await message.edit("☻/  Hello! 🌷\n/▌\n/ \\ ")

add_command_help("greetings", [[".lslove", "Play a short heart animation."], [".hi", "Send a simple greeting."]])
