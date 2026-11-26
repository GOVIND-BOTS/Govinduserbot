from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import OWNER_ID, ALIVE_PIC
from Zaid import app, API_ID, API_HASH, clients, ids

START_TEXT = (
    "✘ Heya, Master!\n\n"
    "I can help you manage your connected user clients.\n\n"
    "Use /clone followed by a valid Pyrogram string session "
    "to connect an account you own."
)


@app.on_message(filters.user(OWNER_ID) & filters.command("start"))
async def hello(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Updates Channel", url="https://t.me/GOVIND_USERBOT_UPDATE")],
        [InlineKeyboardButton("Support Group", url="https://t.me/GOVIND_MP_USERBOT_SPPORT")],
    ])
    if ALIVE_PIC:
        await client.send_photo(message.chat.id, ALIVE_PIC, caption=START_TEXT, reply_markup=buttons)
    else:
        await message.reply_text(START_TEXT, reply_markup=buttons)


@app.on_message(filters.user(OWNER_ID) & filters.command("clone"))
async def clone(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Usage: /clone YOUR_STRING_SESSION")

    session_string = message.text.split(None, 1)[1].strip()
    try:
        await message.delete()
    except Exception:
        pass

    status = await client.send_message(message.chat.id, "Connecting your user account...")
    user_client = Client(
        name=f"clone_{message.from_user.id}_{len(clients) + 1}",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session_string,
        plugins={"root": "Zaid/modules"},
    )
    try:
        await user_client.start()
        user = await user_client.get_me()
        clients.append(user_client)
        if user.id not in ids:
            ids.append(user.id)
        await status.edit_text(
            f"Connected successfully: {user.first_name} ({user.id})."
        )
    except Exception as exc:
        try:
            await user_client.stop()
        except Exception:
            pass
        await status.edit_text(
            f"Could not connect session: {type(exc).__name__}"
        )
