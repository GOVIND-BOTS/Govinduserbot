"""Run a network speed test (can take a minute)."""
import asyncio
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

def _run_speedtest():
    import speedtest
    tester = speedtest.Speedtest()
    tester.get_best_server()
    download = tester.download()
    upload = tester.upload()
    return tester.results.ping, download, upload, tester.results.server.get("name", "Unknown"), tester.results.client.get("isp", "Unknown")

@Client.on_message(filters.command("speedtest", ".") & filters.me)
async def speed_test(_, message):
    mode = message.command[1].lower() if len(message.command) > 1 else "text"
    if mode not in ("text", "image", "file"):
        return await message.edit("Usage: `.speedtest [text|image|file]`")
    status = await message.edit("Running speed test. Please wait...")
    try:
        ping, download, upload, server, isp = await asyncio.to_thread(_run_speedtest)
        result = (f"**Internet speed test**\n**Ping:** {ping:.2f} ms\n"
                  f"**Download:** {download / 1_000_000:.2f} Mbps\n"
                  f"**Upload:** {upload / 1_000_000:.2f} Mbps\n"
                  f"**Server:** {server}\n**ISP:** {isp}")
        await status.edit(result)
    except Exception as exc:
        await status.edit(f"Speed test failed: `{exc}`")

add_command_help("legend_speedtest", [[".speedtest [text]", "Measure server download, upload and ping speeds."]])
