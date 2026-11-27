import asyncio
from io import BytesIO

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.helper.PyroHelpers import ReplyCheck
from ICC.modules.help import add_command_help


async def make_carbon(code):
    url = "https://carbonara.vercel.app/api/cook"
    timeout = aiohttp.ClientTimeout(total=60)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.post(url, json={"code": code}) as resp:
            if resp.status != 200:
                detail = (await resp.text())[:300]
                raise RuntimeError(
                    f"Carbon API returned HTTP {resp.status}: {detail}"
                )

            image_data = await resp.read()
            if not image_data:
                raise RuntimeError("Carbon API returned an empty image.")

    image = BytesIO(image_data)
    image.name = "carbon.png"
    return image


@Client.on_message(filters.command("carbon", ".") & filters.me)
async def carbon_func(client: Client, message: Message):
    text = (
        message.text.split(None, 1)[1]
        if message.text and len(message.command) > 1
        else None
    )
    if message.reply_to_message:
        text = (
            message.reply_to_message.text
            or message.reply_to_message.caption
        )

    if not text:
        return await message.delete()

    status = await message.edit_text("`Preparing Carbon . . .`")
    carbon = None

    try:
        carbon = await make_carbon(text)
        await status.edit_text("`Uploading . . .`")
        await client.send_photo(
            message.chat.id,
            carbon,
            caption=f"**Carbonised by** {client.me.mention}",
            reply_to_message_id=ReplyCheck(message),
        )
    except Exception as exc:
        await status.edit_text(f"**Carbon error:** `{str(exc)[:700]}`")
        return
    finally:
        if carbon:
            carbon.close()

    await status.delete()


add_command_help(
    "carbon",
    [
        ["carbon <reply>", "Carbonize text with default settings."],
    ],
)
