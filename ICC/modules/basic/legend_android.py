

import aiohttp

from pyrogram import Client, filters
from ICC.modules.help import add_command_help


BASE = "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master"


async def _fetch_json(url):
    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()


@Client.on_message(filters.command("magisk", ".") & filters.me)
async def magisk_releases(_, message):
    status = await message.edit("Fetching Magisk releases...")
    try:
        data = {}
        for channel in ("stable", "beta", "canary"):
            data[channel.title()] = await _fetch_json(
                f"https://raw.githubusercontent.com/topjohnwu/magisk-files/master/{channel}.json"
            )
        lines = ["**Latest Magisk releases**"]
        for channel, payload in data.items():
            magisk = payload.get("magisk", {})
            version = magisk.get("version", "Unknown")
            link = magisk.get("link")
            note = magisk.get("note")
            item = f"**{channel}:** v{version}"
            if link:
                item += f" — [APK]({link})"
            if note:
                item += f" | [Changelog]({note})"
            lines.append(item)
        await status.edit("\\n".join(lines), disable_web_page_preview=True)
    except Exception as exc:
        await status.edit(f"Magisk API error: `{exc}`")


@Client.on_message(filters.command("device", ".") & filters.me)
async def android_device(_, message):
    query = message.text.split(maxsplit=1)
    codename = query[1].strip() if len(query) > 1 else ""
    if not codename and message.reply_to_message:
        codename = (message.reply_to_message.text or message.reply_to_message.caption or "").strip().split()[0]
    if not codename:
        return await message.edit("Usage: `.device <codename>`")
    try:
        data = await _fetch_json(f"{BASE}/by_device.json")
        results = data.get(codename.lower()) or data.get(codename)
        if not results:
            return await message.edit(f"No certified Android device found for `{codename}`.")
        lines = [f"**Device results for {codename}:**"]
        for item in results[:8]:
            lines.append(
                f"**Brand:** {item.get('brand', '—')}\n"
                f"**Name:** {item.get('name', '—')}\n"
                f"**Model:** {item.get('model', '—')}"
            )
        await message.edit("\\n\\n".join(lines))
    except Exception as exc:
        await message.edit(f"Device lookup failed: `{exc}`")


@Client.on_message(filters.command("codename", ".") & filters.me)
async def android_codename(_, message):
    args = message.text.split(maxsplit=2)
    query = args[1] if len(args) > 1 else ""
    if not query and message.reply_to_message:
        query = message.reply_to_message.text or message.reply_to_message.caption or ""
    parts = query.split(maxsplit=1)
    if len(parts) < 2:
        return await message.edit("Usage: `.codename <brand> <device name>`")
    brand, device = parts[0].lower(), parts[1].lower()
    try:
        data = await _fetch_json(f"{BASE}/by_brand.json")
        devices = next((v for k, v in data.items() if k.lower() == brand), None)
        if not devices:
            return await message.edit(f"Brand `{brand}` not found.")
        matches = [
            item for item in devices
            if item.get("name", "").lower() == device
            or item.get("model", "").lower() == device
        ][:8]
        if not matches:
            return await message.edit(f"No matching device found for `{brand} {device}`.")
        lines = [f"**Codename results for {brand} {device}:**"]
        for item in matches:
            lines.append(
                f"**Device:** `{item.get('device', '—')}`\n"
                f"**Name:** {item.get('name', '—')}\n"
                f"**Model:** {item.get('model', '—')}"
            )
        await message.edit("\\n\\n".join(lines))
    except Exception as exc:
        await message.edit(f"Codename lookup failed: `{exc}`")


@Client.on_message(filters.command(["id", "getid"], ".") & filters.me)
async def get_ids(_, message):
    reply = message.reply_to_message
    lines = [f"**Chat ID:** `{message.chat.id}`"]
    if reply:
        if reply.from_user:
            lines.append(f"**User ID:** `{reply.from_user.id}`")
        elif reply.sender_chat:
            lines.append(f"**Sender chat ID:** `{reply.sender_chat.id}`")
        media = reply.document or reply.photo or reply.video or reply.audio or reply.voice or reply.sticker
        if media:
            lines.append(f"**Media file ID:** `{media.file_id}`")
            lines.append(f"**File unique ID:** `{media.file_unique_id}`")
    await message.edit("\\n".join(lines))


add_command_help(
    "legend_android",
    [
        [".magisk", "Get latest Magisk stable, beta and canary releases."],
        [".device <codename>", "Look up certified Android devices by codename."],
        [".codename <brand> <device>", "Find an Android device codename."],
        [".id", "Show the current chat ID; reply to include user and media IDs."],
    ],
)
