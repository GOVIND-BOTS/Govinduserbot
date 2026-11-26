import time
from datetime import datetime

from pyrogram import Client

from config import (
    API_ID, API_HASH, SUDO_USERS, OWNER_ID, BOT_TOKEN,
    STRING_SESSION1, STRING_SESSION2, STRING_SESSION3, STRING_SESSION4,
    STRING_SESSION5, STRING_SESSION6, STRING_SESSION7, STRING_SESSION8,
    STRING_SESSION9, STRING_SESSION10,
)

StartTime = time.time()
START_TIME = datetime.now()
CMD_HELP = {}
SUDO_USER = SUDO_USERS
clients = []
ids = []

if OWNER_ID and OWNER_ID not in SUDO_USERS:
    SUDO_USERS.append(OWNER_ID)

if not API_ID or not API_HASH:
    raise RuntimeError("API_ID and API_HASH are required. Set both in hosting environment.")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Set it in hosting environment.")

app = Client(
    name="app",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins={"root": "Zaid/modules/bot"},
    in_memory=True,
)

SESSION_STRINGS = [
    ("one", STRING_SESSION1), ("two", STRING_SESSION2),
    ("three", STRING_SESSION3), ("four", STRING_SESSION4),
    ("five", STRING_SESSION5), ("six", STRING_SESSION6),
    ("seven", STRING_SESSION7), ("eight", STRING_SESSION8),
    ("nine", STRING_SESSION9), ("ten", STRING_SESSION10),
]

for name, session_string in SESSION_STRINGS:
    if session_string:
        clients.append(Client(
            name=name,
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
            plugins={"root": "Zaid/modules"},
        ))
        print(f"User client configured: {name}")
