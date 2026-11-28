import asyncio
import io
import random

from PIL import Image, ImageEnhance, ImageOps
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


def fry_image(image: Image.Image) -> Image.Image:
    colors = (
        tuple(random.randint(40, 190) for _ in range(3)),
        tuple(random.randint(170, 255) for _ in range(3)),
    )
    image = image.convert("RGB")
    width, height = image.size
    image = image.resize((max(1, int(width * 0.72)), max(1, int(height * 0.72))), Image.Resampling.BILINEAR)
    image = image.resize((width, height), Image.Resampling.BICUBIC)
    image = ImageOps.posterize(image, random.randint(3, 6))
    overlay = ImageEnhance.Contrast(image.split()[0]).enhance(1.7)
    overlay = ImageOps.colorize(overlay, colors[0], colors[1])
    image = Image.blend(image, overlay, 0.28)
    return ImageEnhance.Sharpness(image).enhance(12)


@Client.on_message(filters.command("deepfry", ".") & filters.me)
async def deepfry(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not (reply.photo or (reply.document and (reply.document.mime_type or "").startswith("image/"))):
        return await message.edit("Reply to a static image or photo. Animated media is not supported.")
    try:
        level = int(message.command[1]) if len(message.command) > 1 else 1
        if not 1 <= level <= 5:
            raise ValueError
    except ValueError:
        return await message.edit("Usage: `.deepfry [1-5]`")
    status = await message.edit("Deep-frying image…")
    source = output = None
    try:
        source = await client.download_media(reply, file_name="downloads/deepfry_source")
        with Image.open(source) as original:
            if original.width * original.height > 20_000_000:
                raise ValueError("Image is too large (20 megapixels maximum).")
            result = original.copy()
        for _ in range(level):
            result = await asyncio.to_thread(fry_image, result)
        output = io.BytesIO()
        output.name = "deepfried.jpg"
        result.save(output, "JPEG", quality=88)
        output.seek(0)
        await client.send_photo(message.chat.id, output, reply_to_message_id=reply.id)
        await status.delete()
    except Exception as exc:
        await status.edit(f"**Deepfry error:** `{str(exc)[:350]}`")
    finally:
        if source:
            import os
            if os.path.isfile(source):
                os.remove(source)
        if output:
            output.close()


add_command_help("deepfry", [
    [".deepfry [1-5]", "Apply a deep-fried effect to a replied static image."],
])
