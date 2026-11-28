import io

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("img", ".") & filters.me)
async def image_search(client: Client, message: Message):
    query = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    if not query and message.reply_to_message:
        query = message.reply_to_message.text or message.reply_to_message.caption or ""
    if not query:
        return await message.edit("Usage: `.img <search terms>`")
    status = await message.edit("Searching Wikimedia Commons…")
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": "6",
        "gsrlimit": "3",
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": "900",
        "format": "json",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=35)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://commons.wikimedia.org/w/api.php", params=params) as response:
                data = await response.json(content_type=None)
                if response.status != 200:
                    raise RuntimeError(f"Wikimedia HTTP {response.status}")
            pages = list(data.get("query", {}).get("pages", {}).values())
            if not pages:
                return await status.edit("No images found.")
            sent = 0
            for page in pages:
                info = (page.get("imageinfo") or [{}])[0]
                image_url = info.get("thumburl") or info.get("url")
                if not image_url:
                    continue
                async with session.get(image_url) as image_response:
                    if image_response.status != 200:
                        continue
                    raw = await image_response.read()
                if len(raw) > 8 * 1024 * 1024:
                    continue
                photo = io.BytesIO(raw)
                photo.name = "commons_image.jpg"
                try:
                    await client.send_photo(
                        message.chat.id,
                        photo,
                        caption=page.get("title", "Wikimedia Commons image")[:900],
                    )
                    sent += 1
                except Exception:
                    pass
                finally:
                    photo.close()
            await status.delete() if sent else await status.edit("No supported images could be sent.")
    except Exception as exc:
        await status.edit(f"**Image search error:** `{str(exc)[:400]}`")


add_command_help("images", [
    [".img <query>", "Search Wikimedia Commons and send up to three image results."],
])
