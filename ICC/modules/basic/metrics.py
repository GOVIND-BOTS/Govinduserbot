import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


class Custom(dict):
    def __missing__(self, key):
        return 0


@Client.on_message(filters.command("wordcount", ".") & filters.me)
async def word_count(bot: Client, message: Message):
    await message.delete()
    words = Custom()
    progress = await bot.send_message(message.chat.id, "Processed 0 messages...")
    total = 0

    async for msg in bot.get_chat_history(message.chat.id, limit=1000):
        total += 1
        if total % 100 == 0:
            await progress.edit_text(f"Processed {total} messages...")
            await asyncio.sleep(0.5)
        content = msg.text or msg.caption
        if content:
            for word in content.split():
                words[word.lower()] += 1

    freq = sorted(words, key=words.get, reverse=True)
    output = "Word Counter\n"
    for index, word in enumerate(freq[:25], start=1):
        output += f"{index}. {words[word]}: {word}\n"
    if not freq:
        output += "No text messages found."

    await progress.edit_text(output)


add_command_help(
    "metrics",
    [[".wordcount", "Count the most used words in the last 1000 messages."]],
)
