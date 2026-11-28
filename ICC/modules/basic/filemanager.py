import os
from pathlib import Path

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


ROOT = Path.cwd().resolve()


def safe_path(value: str = ".") -> Path:
    target = (ROOT / value).resolve()
    if target != ROOT and ROOT not in target.parents:
        raise ValueError("Path must stay inside the userbot project directory.")
    return target


@Client.on_message(filters.command("ls", ".") & filters.me)
async def list_files(client: Client, message: Message):
    value = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else "."
    try:
        path = safe_path(value)
        if not path.exists():
            return await message.edit("Path not found.")
        if path.is_file():
            stat = path.stat()
            return await message.edit(
                f"**File:** `{path.relative_to(ROOT)}`\n"
                f"**Size:** `{stat.st_size:,} bytes`"
            )
        entries = sorted(path.iterdir(), key=lambda item: (item.is_file(), item.name.lower()))
        lines = [f"{'📁' if item.is_dir() else '📄'} `{item.name}`" for item in entries[:80]]
        text = f"**Contents of** `{path.relative_to(ROOT) if path != ROOT else '.'}`\n"
        text += "\n".join(lines) if lines else "_Empty directory_"
        if len(text) > 3900:
            text = text[:3850] + "\n… list truncated"
        await message.edit(text)
    except Exception as exc:
        await message.edit(f"**File manager error:** `{str(exc)[:300]}`")


@Client.on_message(filters.command("mkdir", ".") & filters.me)
async def make_directory(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Usage: `.mkdir folder_name`")
    try:
        path = safe_path(" ".join(message.command[1:]))
        path.mkdir(parents=True, exist_ok=False)
        await message.edit(f"Created directory: `{path.relative_to(ROOT)}`")
    except FileExistsError:
        await message.edit("That path already exists.")
    except Exception as exc:
        await message.edit(f"**Error:** `{str(exc)[:300]}`")


@Client.on_message(filters.command("rmfile", ".") & filters.me)
async def remove_file(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Usage: `.rmfile file_path` (files only)")
    try:
        path = safe_path(" ".join(message.command[1:]))
        if not path.exists() or not path.is_file():
            return await message.edit("File not found. Directories cannot be removed with this command.")
        path.unlink()
        await message.edit(f"Deleted file: `{path.relative_to(ROOT)}`")
    except Exception as exc:
        await message.edit(f"**Error:** `{str(exc)[:300]}`")


add_command_help("filemanager", [
    [".ls [path]", "List project files or show file size."],
    [".mkdir <name>", "Create a directory inside the project."],
    [".rmfile <path>", "Delete a file inside the project (directories are protected)."],
])
