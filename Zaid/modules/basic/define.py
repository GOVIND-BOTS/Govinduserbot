import asyncio
from urllib.parse import quote

from pyrogram import Client, filters
from pyrogram.types import Message

from Zaid.helper.aiohttp_helper import AioHttp
from Zaid.modules.help import add_command_help


@Client.on_message(filters.command(["define", "dict"], ".") & filters.me)
async def define(bot: Client, message: Message):
    if len(message.command) > 1:
        word = " ".join(message.command[1:]).strip()
    elif message.reply_to_message:
        word = (message.reply_to_message.text or message.reply_to_message.caption or "").strip()
    else:
        await message.edit("Please provide a word to define.")
        return

    if not word:
        return await message.edit("Please provide a word to define.")

    try:
        result = await AioHttp.get_json(
            "https://api.dictionaryapi.dev/api/v2/entries/en/" + quote(word)
        )
    except Exception as exc:
        return await message.edit(f"Dictionary lookup failed: {type(exc).__name__}")

    if not isinstance(result, list) or not result:
        return await message.edit("No definition found for that word.")

    entry = result[0]
    lines = [f"**{entry.get('word', word)}**"]
    for meaning in entry.get("meanings", []):
        part = meaning.get("partOfSpeech", "Meaning")
        lines.append(f"\n**{part.title()}**")
        for definition in meaning.get("definitions", [])[:3]:
            value = definition.get("definition")
            if value:
                lines.append("• " + value)
            example = definition.get("example")
            if example:
                lines.append("  Example: " + example)

    output = "\n".join(lines)
    if len(output) > 4000:
        output = output[:3990] + "..."
    await message.edit_text(output)


add_command_help(
    "dictionary",
    [[".define | .dict [word]", "Look up an English word in the dictionary."]],
)
