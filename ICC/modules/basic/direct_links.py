import re
from urllib.parse import parse_qs, urlparse

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


URL_RE = re.compile(r"https?://[^\s<>]+", re.I)


def direct_url(value: str):
    parsed = urlparse(value.strip().rstrip(".,)"))
    host = (parsed.hostname or "").lower()
    if host == "drive.google.com":
        match = re.search(r"/file/d/([\w-]+)", parsed.path)
        file_id = match.group(1) if match else parse_qs(parsed.query).get("id", [None])[0]
        if file_id:
            return f"https://drive.google.com/uc?export=download&id={file_id}"
    if host in {"github.com", "www.github.com"}:
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 5 and parts[2] == "blob":
            return f"https://raw.githubusercontent.com/{parts[0]}/{parts[1]}/{'/'.join(parts[3:])}"
    return None


@Client.on_message(filters.command("direct", ".") & filters.me)
async def direct_link(client: Client, message: Message):
    source = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    if not source and message.reply_to_message:
        source = message.reply_to_message.text or message.reply_to_message.caption or ""
    links = URL_RE.findall(source)
    if not links:
        return await message.edit("Usage: `.direct <Google Drive/GitHub URL>` or reply to a message containing a link.")
    results = []
    for link in links[:10]:
        resolved = direct_url(link)
        results.append(f"**Direct:** {resolved}" if resolved else f"Not supported: {link}")
    await message.edit("\n\n".join(results), disable_web_page_preview=True)


add_command_help("direct_links", [
    [".direct <url>", "Convert supported Google Drive and GitHub file links to direct download URLs."],
])
