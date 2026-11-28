import asyncio
import os
import shutil
import tempfile
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("collage", ".") & filters.me)
async def video_collage(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not (reply.video or reply.animation or reply.document):
        return await message.edit("Reply to a video or GIF to create a frame collage.")
    if not shutil.which("ffmpeg"):
        return await message.edit("FFmpeg is not installed on this server.")
    try:
        grid = int(message.command[1]) if len(message.command) > 1 else 3
        if not 1 <= grid <= 5:
            raise ValueError
    except ValueError:
        return await message.edit("Usage: `.collage [1-5]`")
    status = await message.edit("Extracting frames…")
    with tempfile.TemporaryDirectory(prefix="icc_collage_") as folder:
        source = str(Path(folder) / "source_media")
        output = str(Path(folder) / "collage.jpg")
        try:
            await client.download_media(reply, file_name=source)
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-i", source, "-vf",
                f"thumbnail,scale=320:-1,tile={grid}x{grid}",
                "-frames:v", "1", output,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
            if process.returncode != 0 or not os.path.isfile(output):
                detail = stderr.decode(errors="ignore")[-500:]
                raise RuntimeError(detail or "FFmpeg could not process this media.")
            await client.send_photo(message.chat.id, output, reply_to_message_id=reply.id)
            await status.delete()
        except asyncio.TimeoutError:
            await status.edit("Collage timed out (120 seconds).")
        except Exception as exc:
            await status.edit(f"**Collage error:** `{str(exc)[:500]}`")


add_command_help("collage", [
    [".collage [1-5]", "Create a frame-grid collage from a replied video or GIF (requires FFmpeg)."],
])
