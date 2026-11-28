"""Create an RGB-shift glitch effect from a replied photo."""
import os
import tempfile

from PIL import Image, ImageChops
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("glitch", ".") & filters.me)
async def glitch_photo(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.photo:
        return await message.edit_text("Reply to a photo with `.glitch [1-12]`.")
    try:
        strength = int(message.command[1]) if len(message.command) > 1 else 4
    except ValueError:
        return await message.edit_text("Strength must be a number from 1 to 12.")
    if not 1 <= strength <= 12:
        return await message.edit_text("Strength must be between 1 and 12.")

    status = await message.edit_text("Creating glitch effect...")
    source = output = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
            source = temp.name
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
            output = temp.name
        downloaded = await client.download_media(reply, file_name=source)
        if not downloaded:
            return await status.edit_text("Could not download the replied photo.")
        with Image.open(downloaded) as original:
            image = original.convert("RGB")
        red, green, blue = image.split()
        red = ImageChops.offset(red, strength, 0)
        blue = ImageChops.offset(blue, -strength, 0)
        Image.merge("RGB", (red, green, blue)).save(output, "PNG")
        await message.reply_photo(output, caption="RGB glitch effect")
        await status.delete()
    except Exception as exc:
        await status.edit_text(f"Glitch failed: `{str(exc)[:250]}`")
    finally:
        for path in (source, output):
            if path and os.path.exists(path):
                os.remove(path)


add_command_help("glitch", [[".glitch [1-12] (reply to photo)", "Apply an RGB-shift glitch effect to a replied photo."]])
