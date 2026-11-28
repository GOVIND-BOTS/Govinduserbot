"""One-shot delayed message scheduler for ICC Userbot.

Feature adapted for ICC Userbot from the source schedule plugin.
Scheduled tasks are held in memory and are lost if the process restarts.
"""
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from ICC.modules.help import add_command_help


TASKS = {}


@Client.on_message(filters.command("schd", ".") & filters.me)
async def schedule_message(client: Client, message: Message):
    if len(message.command) < 3:
        return await message.edit_text("Usage: `.schd <seconds> <message>`")
    try:
        delay = int(message.command[1])
    except ValueError:
        return await message.edit_text("Time must be a number of seconds.")
    if not 5 <= delay <= 604800:
        return await message.edit_text("Delay must be between 5 seconds and 7 days.")
    body = message.text.split(maxsplit=2)[2]
    chat_id = message.chat.id
    previous = TASKS.get(chat_id)
    if previous and not previous.done():
        previous.cancel()
    status = await message.edit_text(f"Message scheduled in {delay} seconds.")

    async def deliver():
        try:
            await asyncio.sleep(delay)
            await client.send_message(chat_id, body, disable_web_page_preview=True)
            await status.delete()
        except asyncio.CancelledError:
            return
        except Exception as exc:
            try:
                await status.edit_text(f"Scheduled message failed: {str(exc)[:200]}")
            except Exception:
                pass
        finally:
            if TASKS.get(chat_id) is asyncio.current_task():
                TASKS.pop(chat_id, None)

    TASKS[chat_id] = asyncio.create_task(deliver())


@Client.on_message(filters.command("schdcancel", ".") & filters.me)
async def cancel_schedule(client: Client, message: Message):
    task = TASKS.pop(message.chat.id, None)
    if task and not task.done():
        task.cancel()
        await message.edit_text("Scheduled message cancelled.")
    else:
        await message.edit_text("No scheduled message in this chat.")


add_command_help("schedule", [
    [".schd <seconds> <message>", "Send a one-shot message after the chosen delay (5 seconds to 7 days)."],
    [".schdcancel", "Cancel the pending scheduled message in this chat."],
])
