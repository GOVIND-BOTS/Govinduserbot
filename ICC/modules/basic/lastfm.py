import os

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


@Client.on_message(filters.command("lastfm", ".") & filters.me)
async def lastfm_recent(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit("Usage: `.lastfm <last.fm_username>`")
    api_key = os.getenv("LASTFM_API_KEY")
    if not api_key:
        return await message.edit("Set the LASTFM_API_KEY environment variable first.")
    username = message.command[1].strip()
    status = await message.edit("Fetching Last.fm listening activity…")
    params = {
        "method": "user.getrecenttracks",
        "user": username,
        "api_key": api_key,
        "format": "json",
        "limit": "1",
    }
    try:
        timeout = aiohttp.ClientTimeout(total=20)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get("https://ws.audioscrobbler.com/2.0/", params=params) as response:
                data = await response.json(content_type=None)
                if response.status != 200 or "error" in data:
                    raise RuntimeError(data.get("message", f"Last.fm HTTP {response.status}"))
        tracks = data.get("recenttracks", {}).get("track", [])
        if not tracks:
            return await status.edit("No recent tracks found for that account.")
        track = tracks[0]
        artist = track.get("artist", {}).get("#text", "Unknown artist")
        title = track.get("name", "Unknown track")
        album = track.get("album", {}).get("#text", "Unknown album")
        now = " **(Now playing)**" if track.get("@attr", {}).get("nowplaying") == "true" else ""
        url = track.get("url", "")
        await status.edit(
            f"**Last.fm — {username}**\n"
            f"🎵 [{title}]({url}){now}\n"
            f"👤 {artist}\n💿 {album}",
            disable_web_page_preview=True,
        )
    except Exception as exc:
        await status.edit(f"**Last.fm error:** `{str(exc)[:400]}`")


add_command_help("lastfm", [
    [".lastfm <username>", "Show the latest scrobbled track (requires LASTFM_API_KEY)."],
])
