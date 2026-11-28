import re
import aiohttp
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

@Client.on_message(filters.command("filext", ".") & filters.me)
async def file_extension_info(_, message):
    ext = " ".join(message.command[1:]).strip().lower().lstrip(".")
    if not ext or not re.fullmatch(r"[a-z0-9]{1,12}", ext):
        return await message.edit("Usage: `.filext <extension>` (example: `.filext py`)")
    status = await message.edit("Looking up file extension...")
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"https://www.fileext.com/file-extension/{ext}.html") as resp:
                if resp.status != 200:
                    return await status.edit(f"No information found for `.{ext}` (HTTP {resp.status}).")
                html = await resp.text()
        soup = BeautifulSoup(html, "html.parser")
        cells = soup.find_all("td", colspan="3")
        description = cells[-1].get_text(" ", strip=True) if cells else ""
        if not description:
            description = soup.find("meta", attrs={"name": "description"})
            description = description.get("content", "") if description else ""
        if not description:
            return await status.edit(f"No description found for `.{ext}`.")
        await status.edit(f"**Extension:** `.{ext}`\n**Description:** {description[:2500]}")
    except Exception as exc:
        await status.edit(f"Lookup failed: `{exc}`")

add_command_help("filext", [[".filext <extension>", "Get information about a file extension."]])
