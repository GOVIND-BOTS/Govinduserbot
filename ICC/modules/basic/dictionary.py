import aiohttp
from urllib.parse import quote
from pyrogram import Client, filters
from ICC.modules.help import add_command_help


@Client.on_message(filters.command(["define", "meaning"], ".") & filters.me)
async def define_word(_, message):
    word = " ".join(message.command[1:]).strip()
    if not word and message.reply_to_message:
        source = message.reply_to_message.text or message.reply_to_message.caption or ""
        word = source.split()[0] if source.split() else ""
    if not word:
        return await message.edit_text("Usage: .define <English word>")
    if len(word) > 60 or " " in word:
        return await message.edit_text("Please enter one English word (maximum 60 characters).")
    status = await message.edit_text(f"Looking up {word}…")
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}") as response:
                data = await response.json(content_type=None)
                if response.status != 200:
                    raise ValueError("No definition found for that word.")
        entry = data[0]
        pronunciations = []
        for item in entry.get("phonetics", []):
            sound = item.get("text")
            if sound and sound not in pronunciations:
                pronunciations.append(sound)
        lines = [f"📖 **{entry.get('word', word)}**"]
        if pronunciations:
            lines.append(f"**Pronunciation:** {' / '.join(pronunciations[:2])}")
        count = 0
        for meaning in entry.get("meanings", []):
            for definition in meaning.get("definitions", []):
                lines.append(f"\n**{meaning.get('partOfSpeech', 'Meaning')}:** {definition.get('definition', '')}")
                if definition.get("example"):
                    lines.append(f"Example: {definition['example']}")
                count += 1
                if count >= 4:
                    break
            if count >= 4:
                break
        lines.append("\n_Source: Free Dictionary API_")
        await status.edit_text("\n".join(lines))
    except Exception as exc:
        await status.edit_text(f"Dictionary lookup failed: {str(exc)[:250]}")


add_command_help("dictionary", [
    [".define <word>", "Find an English word's meaning and pronunciation."],
    [".meaning <word>", "Alias for .define."],
])
