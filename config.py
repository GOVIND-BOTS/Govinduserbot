import os
from dotenv import load_dotenv

if os.path.exists("local.env"):
    load_dotenv("local.env")
else:
    load_dotenv()


def _int_env(name, default=0):
    value = os.getenv(name, str(default)).strip()
    if not value:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer.") from exc


def _user_ids(value):
    result = []
    for item in (value or "").replace(",", " ").split():
        try:
            user_id = int(item)
        except ValueError:
            continue
        if user_id not in result:
            result.append(user_id)
    return result


API_ID = _int_env("API_ID", 6435225)
API_HASH = os.getenv("API_HASH", "").strip()
SUDO_USERS = _user_ids(os.getenv("SUDO_USERS", ""))
OWNER_ID = _int_env("OWNER_ID", 0)
MONGO_URL = os.getenv("MONGO_URL") or None
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ALIVE_PIC = os.getenv("ALIVE_PIC", "https://te.legra.ph/file/80eda2848fdeb52b191ad.jpg").strip()
ALIVE_TEXT = os.getenv("ALIVE_TEXT")
PM_LOGGER = os.getenv("PM_LOGGER")
LOG_GROUP = os.getenv("LOG_GROUP")
GIT_TOKEN = os.getenv("GIT_TOKEN")
REPO_URL = os.getenv("REPO_URL", "https://github.com/GOVIND-BOTS/Govinduserbot")
BRANCH = os.getenv("BRANCH", "master")

STRING_SESSION1 = os.getenv("STRING_SESSION1", "").strip()
STRING_SESSION2 = os.getenv("STRING_SESSION2", "").strip()
STRING_SESSION3 = os.getenv("STRING_SESSION3", "").strip()
STRING_SESSION4 = os.getenv("STRING_SESSION4", "").strip()
STRING_SESSION5 = os.getenv("STRING_SESSION5", "").strip()
STRING_SESSION6 = os.getenv("STRING_SESSION6", "").strip()
STRING_SESSION7 = os.getenv("STRING_SESSION7", "").strip()
STRING_SESSION8 = os.getenv("STRING_SESSION8", "").strip()
STRING_SESSION9 = os.getenv("STRING_SESSION9", "").strip()
STRING_SESSION10 = os.getenv("STRING_SESSION10", "").strip()
