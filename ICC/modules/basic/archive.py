"""Safe reply-based ZIP tools for ICC Userbot.

ICC USERBOT module.
"""
import asyncio
import os
import tempfile
import zipfile

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


def _make_zip(source, target):
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(source, arcname=os.path.basename(source))


def _safe_extract(source, target):
    with zipfile.ZipFile(source) as archive:
        members = [item for item in archive.infolist() if not item.is_dir()]
        if len(members) > 10 or sum(item.file_size for item in members) > 50 * 1024 * 1024:
            raise ValueError("Archive is too large to extract (max 10 files / 50 MB).")
        root = os.path.realpath(target)
        for item in members:
            destination = os.path.realpath(os.path.join(root, item.filename))
            if os.path.commonpath([root, destination]) != root:
                raise ValueError("Unsafe path found inside archive.")
        archive.extractall(target)
        return [os.path.join(target, item.filename) for item in members]


@Client.on_message(filters.command("zip", ".") & filters.me)
async def zip_reply(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.media:
        return await message.edit_text("Reply to a file or media with `.zip`.")
    status = await message.edit_text("Creating ZIP archive...")
    with tempfile.TemporaryDirectory() as folder:
        source = await client.download_media(reply, file_name=folder + "/")
        if not source:
            return await status.edit_text("Could not download the replied media.")
        target = os.path.join(folder, "archive.zip")
        await asyncio.to_thread(_make_zip, source, target)
        await client.send_document(message.chat.id, target, caption="ICC USERBOT • ZIP archive")
    await status.delete()


@Client.on_message(filters.command("unzip", ".") & filters.me)
async def unzip_reply(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply or not reply.document:
        return await message.edit_text("Reply to a ZIP document with `.unzip`.")
    status = await message.edit_text("Extracting archive...")
    with tempfile.TemporaryDirectory() as folder:
        source = await client.download_media(reply, file_name=folder + "/input.zip")
        try:
            extracted = await asyncio.to_thread(_safe_extract, source, os.path.join(folder, "out"))
        except (zipfile.BadZipFile, ValueError) as exc:
            return await status.edit_text(f"Cannot extract archive: {exc}")
        if not extracted:
            return await status.edit_text("The archive contains no files.")
        for path in extracted:
            if os.path.isfile(path):
                await client.send_document(message.chat.id, path)
    await status.delete()


add_command_help("archive", [
    [".zip (reply)", "Compress replied media into a ZIP archive."],
    [".unzip (reply)", "Safely extract a ZIP archive (up to 10 files / 50 MB)."],
])
