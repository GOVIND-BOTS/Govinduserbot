"""Telegram dice and game animations.

ICC USERBOT module.
"""
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


GAMES = {
    "dice": "🎲",
    "dart": "🎯",
    "basket": "🏀",
    "football": "⚽",
    "slot": "🎰",
    "bowling": "🎳",
}


@Client.on_message(filters.command(list(GAMES), ".") & filters.me)
async def emoji_game(client: Client, message: Message):
    command = message.command[0].lower()
    await client.send_dice(message.chat.id, emoji=GAMES[command], reply_to_message_id=message.reply_to_message.id if message.reply_to_message else None)
    await message.delete()


add_command_help("emojigames", [[f".{name}", f"Send Telegram {name} animation."] for name in GAMES])
