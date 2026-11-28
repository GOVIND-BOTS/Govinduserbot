import asyncio
import os
import shutil
import tempfile
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("compress", ".") & filters.me)
async def compress_video(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not (reply.video or reply.animation or (reply.document and (reply.document.mime_type or "").startswith("video/"))):
        return await message.edit("Reply to a video file to compress it.")
    if not shutil.which("ffmpeg"):
        return await message.edit("FFmpeg is not installed on this server.")
    try:
        crf = int(message.command[1]) if len(message.command) > 1 else 28
        if not 18 <= crf <= 40:
            raise ValueError
    except ValueError:
        return await message.edit("Usage: `.compress [18-40]` (higher value = smaller file/lower quality)")
    status = await message.edit("Downloading video…")
    with tempfile.TemporaryDirectory(prefix="icc_compress_") as folder:
        source = str(Path(folder) / "input_media")
        output = str(Path(folder) / "compressed.mp4")
        try:
            await client.download_media(reply, file_name=source)
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-i", source, "-c:v", "libx264",
                "-preset", "veryfast", "-crf", str(crf), "-c:a", "aac",
                "-b:a", "128k", "-movflags", "+faststart", output,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            _, stderr = await asyncio.wait_for(process.communicate(), timeout=600)
            if process.returncode != 0 or not os.path.isfile(output):
                raise RuntimeError(stderr.decode(errors="ignore")[-500:] or "FFmpeg failed.")
            await status.edit("Uploading compressed video…")
            await client.send_video(message.chat.id, output, reply_to_message_id=reply.id)
            await status.delete()
        except asyncio.TimeoutError:
            await status.edit("Compression timed out (10 minutes).")
        except Exception as exc:
            await status.edit(f"**Compression error:** `{str(exc)[:500]}`")


add_command_help("ffmpeg", [
    [".compress [18-40]", "Compress a replied video using FFmpeg (requires FFmpeg installed)."],
])
