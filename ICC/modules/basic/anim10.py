import asyncio
from collections import deque

from pyrogram import Client, filters
from pyrogram.errors import FloodWait

from ICC.modules.help import add_command_help


async def _play_anim(message, frames, delay=0.5):
    for frame in frames:
        try:
            await message.edit(frame)
        except FloodWait as exc:
            await asyncio.sleep(exc.value)
            try:
                await message.edit(frame)
            except Exception:
                return
        except Exception:
            return
        await asyncio.sleep(delay)


@Client.on_message(filters.command("indflag", ".") & filters.me)
async def indian_flag(_, message):
    frames = [
        "🇮🇳 **INDIAN FLAG** 🇮🇳",
        "🟧🟧🟧🟧🟧🟧🟧🟧🟧\n⬜⬜⬜⬜🔵⬜⬜⬜⬜\n🟩🟩🟩🟩🟩🟩🟩🟩🟩",
        "🟧🟧🟧🟧🟧🟧🟧🟧🟧\n⬜⬜⬜🔵🔵🔵⬜⬜⬜\n🟩🟩🟩🟩🟩🟩🟩🟩🟩",
        "🧡 🤍 💚\n\n**PROUD TO BE INDIAN! 🇮🇳**",
    ]
    await _play_anim(message, frames, 0.7)


@Client.on_message(filters.command("yo", ".") & filters.me)
async def yo_animation(_, message):
    await _play_anim(message, ["yo", "yoo", "yooo", "yoooo", "yooooo", "yoooooo", "YOOOOOO! 😎"], 0.25)


@Client.on_message(filters.command("evil", ".") & filters.me)
async def evil_animation(_, message):
    frames = [
        "😒 You know I'm a good **PERSON** 😏",
        "BUT... 😡",
        "Don't give me a reason! 😠",
        "To show you my... 😎",
        "**😈 EVIL SIDE 😈**",
    ]
    await _play_anim(message, frames, 0.8)


@Client.on_message(filters.command("gnt", ".") & filters.me)
async def good_night(_, message):
    await message.edit(
        "｡♥｡･ﾟ♡ﾟ･｡♥｡･｡･｡･｡♥｡･\n"
        "╱╱╱╱╱╱╱╭╮╱╱╱╭╮╱╭╮╭╮\n"
        "╭━┳━┳━┳╯┃╭━┳╋╋━┫╰┫╰╮\n"
        "┃╋┃╋┃╋┃╋┃┃┃┃┃┃╋┃┃┃╭┫\n"
        "┣╮┣━┻━┻━╯╰┻━┻╋╮┣┻┻━╯\n"
        "╰━╯╱╱╱╱╱╱╱╱╱╱╰━╯\n"
        "｡♥｡･ﾟ♡ﾟ･｡♥ **GOOD NIGHT** 🌙"
    )


@Client.on_message(filters.command("gmg", ".") & filters.me)
async def good_morning(_, message):
    await message.edit(
        "｡♥｡･ﾟ♡ﾟ･｡♥｡･｡･｡･｡♥｡･｡♥｡･ﾟ♡ﾟ･\n"
        "╱╱╱╱╱╱╱╭╮╱╱╱╱╱╱╱╱╱╱╭╮\n"
        "╭━┳━┳━┳╯┃╭━━┳━┳┳┳━┳╋╋━┳┳━╮\n"
        "┃╋┃╋┃╋┃╋┃┃┃┃┃╋┃╭┫┃┃┃┃┃┃┃╋┃\n"
        "┣╮┣━┻━┻━╯╰┻┻┻━┻╯╰┻━┻┻┻━╋╮┃\n"
        "╰━╯╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╰━╯\n"
        "☀️ **GOOD MORNING!** 🌸"
    )


@Client.on_message(filters.command("hypno", ".") & filters.me)
async def hypnosis(_, message):
    frames = [
        "⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜\n⬜⬜⬜⬜⬜",
        "⬜⬜⬜⬜⬜\n⬜⬜⬛⬜⬜\n⬜⬛⬛⬛⬜\n⬜⬜⬛⬜⬜\n⬜⬜⬜⬜⬜",
        "⬛⬛⬛⬛⬛\n⬛⬜⬜⬜⬛\n⬛⬜⬛⬜⬛\n⬛⬜⬜⬜⬛\n⬛⬛⬛⬛⬛",
        "⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜\n⬛⬜⬛⬜⬛\n⬜⬛⬜⬛⬜",
        "⬛⬛⬛⬛⬛\n⬛⬜⬜⬜⬛\n⬛⬜🔴⬜⬛\n⬛⬜⬜⬜⬛\n⬛⬛⬛⬛⬛",
        "👉 **LOOK HERE** 👈",
    ]
    await _play_anim(message, frames, 0.45)


@Client.on_message(filters.command("candy", ".") & filters.me)
async def candy_animation(_, message):
    candies = deque("🍦🍧🍩🍪🎂🍰🧁🍫🍬🍭")
    frames = []
    for _ in range(16):
        frames.append(" ".join(candies))
        candies.rotate(1)
    await _play_anim(message, frames, 0.35)


@Client.on_message(filters.command("bigoof", ".") & filters.me)
async def big_oof(_, message):
    frames = [
        "┏━━━┓\n┃ O ┃\n┗━━━┛",
        "╭━━━╮╱╱╭━╮\n┃╭━╮┃╱╱┃╭╯\n┃┃╱┃┣━━┫╰╮\n┃╰━╯┃╭╮┃╭╯\n╰━━━┻╯╰┻╯",
        "╭━━━╮╱╱╱╭━╮\n┃╭━╮┃╱╱╱┃╭╯\n┃┃╱┃┣━━┳╯╰╮\n┃┃╱┃┃╭╮┣╮╭╯\n┃╰━╯┃╰╯┃┃┃\n╰━━━┻━━╯╰╯",
        "╭━━━╮╱╱╱╱╭━╮\n┃╭━╮┃╱╱╱╱┃╭╯\n┃┃╱┃┣━━┳━╯╰╮\n┃┃╱┃┃╭╮┣╮╭╯\n┃╰━╯┃╰╯┃┃┃\n╰━━━┻━━╯╰╯",
        "**BIG OOF!** 😂",
    ]
    await _play_anim(message, frames, 0.35)



@Client.on_message(filters.command("f", ".") & filters.me)
async def f_text(_, message):
    text = message.text.partition(" ")[2].strip()
    if not text:
        await message.edit("Usage: `.f <text>`")
        return
    pattern = [
        text * 8,
        text * 8,
        text * 2,
        text * 2,
        text * 2,
        text * 6,
        text * 6,
        text * 2,
        text * 2,
        text * 2,
        text * 2,
        text * 2,
    ]
    await message.edit("\\n".join(pattern))


add_command_help("anim10", [
    [".indflag", "Show the Indian flag animation."],
    [".yo", "Play the yo-to-yoooo animation."],
    [".evil", "Show the funny evil-side animation."],
    [".gnt", "Send the good-night text art."],
    [".gmg", "Send the good-morning text art."],
    [".hypno", "Play the non-explicit hypnosis animation."],
    [".candy", "Rotate a row of candy emojis."],
    [".bigoof", "Play the Big Oof text animation."],
    [".f <text>", "Print the supplied text in an F-style pattern."],
])