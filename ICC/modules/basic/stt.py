import os
import tempfile
from pathlib import Path

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("stt", ".") & filters.me)
async def speech_to_text(client: Client, message: Message):
    reply = message.reply_to_message
    media = reply.voice or reply.audio if reply else None
    if not media:
        return await message.edit("Reply to a voice message or audio file. Set OPENAI_API_KEY to use transcription.")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return await message.edit("OPENAI_API_KEY is not configured on the server.")
    status = await message.edit("Downloading audio for transcription…")
    with tempfile.TemporaryDirectory(prefix="icc_stt_") as folder:
        path = None
        try:
            path = await client.download_media(reply, file_name=str(Path(folder) / "audio"))
            size = os.path.getsize(path)
            if size > 25 * 1024 * 1024:
                raise ValueError("Audio exceeds the 25 MB transcription limit.")
            form = aiohttp.FormData()
            form.add_field("model", "whisper-1")
            with open(path, "rb") as audio:
                form.add_field("file", audio, filename=Path(path).name, content_type=media.mime_type or "application/octet-stream")
                timeout = aiohttp.ClientTimeout(total=180)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers={"Authorization": f"Bearer {api_key}"},
                        data=form,
                    ) as response:
                        payload = await response.json(content_type=None)
                        if response.status != 200:
                            raise RuntimeError(payload.get("error", {}).get("message", f"HTTP {response.status}"))
            transcript = (payload.get("text") or "").strip()
            if not transcript:
                return await status.edit("No speech could be recognized.")
            await status.edit(f"**Transcript:**\n{transcript[:3900]}")
        except Exception as exc:
            await status.edit(f"**STT error:** `{str(exc)[:500]}`")


add_command_help("stt", [
    [".stt", "Transcribe a replied voice/audio message using the configured OPENAI_API_KEY."],
])
