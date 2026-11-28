import io
import textwrap

from PIL import Image, ImageDraw, ImageFont
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


def draw_meme(source: str, top: str, bottom: str):
    with Image.open(source) as opened:
        image = opened.convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    width, height = image.size
    max_chars = max(8, width // 14)

    def draw_caption(value: str, y: int, anchor: str):
        if not value:
            return
        lines = []
        for paragraph in value.splitlines():
            lines.extend(textwrap.wrap(paragraph, max_chars) or [""])
        line_height = 22
        block_height = line_height * len(lines)
        y = max(4, y - block_height // 2) if anchor == "bottom" else y
        for line in lines:
            box = draw.textbbox((0, 0), line, font=font, stroke_width=2)
            x = max(4, (width - (box[2] - box[0])) // 2)
            draw.text((x, y), line, font=font, fill="white", stroke_width=2, stroke_fill="black")
            y += line_height

    draw_caption(top, 12, "top")
    draw_caption(bottom, height - 12, "bottom")
    output = io.BytesIO()
    output.name = "icc_meme.jpg"
    image.save(output, "JPEG", quality=92)
    output.seek(0)
    return output


@Client.on_message(filters.command("meme", ".") & filters.me)
async def make_meme(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not (reply.photo or (reply.document and (reply.document.mime_type or "").startswith("image/"))):
        return await message.edit("Reply to a static image. Usage: `.meme TOP TEXT ; BOTTOM TEXT`")
    raw = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    if not raw:
        return await message.edit("Usage: `.meme TOP TEXT ; BOTTOM TEXT`")
    top, _, bottom = raw.partition(";")
    status = await message.edit("Creating meme…")
    path = None
    result = None
    try:
        path = await client.download_media(reply, file_name="downloads/meme_source")
        result = await __import__("asyncio").to_thread(draw_meme, path, top.strip(), bottom.strip())
        await client.send_photo(message.chat.id, result, reply_to_message_id=reply.id)
        await status.delete()
    except Exception as exc:
        await status.edit(f"**Meme error:** `{str(exc)[:400]}`")
    finally:
        import os
        if path and os.path.isfile(path):
            os.remove(path)
        if result:
            result.close()


add_command_help("memify", [
    [".meme TOP ; BOTTOM", "Write top/bottom captions on a replied image."],
])
