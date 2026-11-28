"""Extract text from a replied image using OCR.Space.

ICC USERBOT module.
Set OCR_SPACE_API_KEY for a personal API key; the public demo key is rate-limited.
"""
import asyncio
import os
import tempfile

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


async def _recognize(path, language, api_key):
    data = aiohttp.FormData()
    data.add_field("language", language)
    data.add_field("isOverlayRequired", "false")
    data.add_field("apikey", api_key)
    with open(path, "rb") as stream:
        data.add_field("file", stream, filename=os.path.basename(path), content_type="application/octet-stream")
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.ocr.space/parse/image", data=data, timeout=90) as response:
                result = await response.json(content_type=None)
    if result.get("IsErroredOnProcessing"):
        raise RuntimeError(str(result.get("ErrorMessage", "OCR processing failed")))
    parsed = result.get("ParsedResults") or []
    return "\n".join(item.get("ParsedText", "") for item in parsed).strip()


@Client.on_message(filters.command("ocr", ".") & filters.me)
async def image_ocr(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.photo and not reply.document:
        return await message.edit_text("Reply to an image with `.ocr [language]`.")
    language = message.command[1] if len(message.command) > 1 else "eng"
    api_key = os.getenv("OCR_SPACE_API_KEY", "helloworld")
    status = await message.edit_text("Reading image text...")
    with tempfile.TemporaryDirectory() as folder:
        path = await client.download_media(reply, file_name=folder + "/")
        try:
            result = await _recognize(path, language, api_key)
        except Exception as exc:
            return await status.edit_text(f"OCR failed: `{str(exc)[:300]}`")
    if not result:
        return await status.edit_text("No readable text was found.")
    await status.edit_text(result[:4000], disable_web_page_preview=True)


add_command_help("ocr", [[".ocr [language] (reply)", "Extract text from a replied image using OCR.Space."]])
