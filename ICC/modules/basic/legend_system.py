"""Basic system information command inspired by LEGENDBOT."""
import platform
import sys
from datetime import datetime
from pyrogram import Client, filters
from ICC.modules.help import add_command_help

@Client.on_message(filters.command(["spc", "sysd"], ".") & filters.me)
async def system_info(_, message):
    uname = platform.uname()
    lines = ["**System information**",
             f"**OS:** `{uname.system} {uname.release}`",
             f"**Machine:** `{uname.machine}`",
             f"**Python:** `{sys.version.split()[0]}`",
             f"**Boot-independent local time:** `{datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')}`"]
    try:
        import psutil
        vm = psutil.virtual_memory()
        lines.extend([f"**CPU cores:** `{psutil.cpu_count(logical=True)}`",
                      f"**CPU usage:** `{psutil.cpu_percent(interval=0.2)}%`",
                      f"**RAM:** `{vm.used / 1024**3:.2f}/{vm.total / 1024**3:.2f} GB ({vm.percent}%)`"])
    except ImportError:
        lines.append("Install psutil for CPU and RAM statistics.")
    await message.edit("\\n".join(lines))

add_command_help("legend_system", [[".spc", "Show basic system and runtime information."], [".sysd", "Show basic system and runtime information."]])
