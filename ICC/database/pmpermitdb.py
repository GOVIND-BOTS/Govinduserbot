from ICC.database import cli

collection = cli["ICC"]["pmpermit"]

PMPERMIT_MESSAGE = (
    "**ᴡᴀʀɴɪɴɢ!⚠️ ᴘʟᴢ ʀᴇᴀᴅ ᴛʜɪꜱ ᴍᴇꜱꜱᴀɢᴇ ᴄᴀʀᴇꜰᴜʟʟʏ..\n\n**"
    "**ɪ'ᴍ ᴢᴀɪᴅ ᴜꜱᴇʀʙᴏᴛ ɪ'ᴍ ʜᴇʀᴇ ᴛᴏ ᴘʀᴏᴛᴇᴄᴛ ᴍʏ ᴍᴀꜱᴛᴇʀ ꜰʀᴏᴍ ꜱᴘᴀᴍᴍᴇʀꜱ.**"
    "**ɪꜰ ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀ ꜱᴘᴀᴍᴍᴇʀ ᴛʜᴇɴ ᴘʟᴢ ᴡᴀɪᴛ!\n\n**"
    "**ᴜɴᴛɪʟ ᴛʜᴇɴ, ᴅᴏɴ'ᴛ ꜱᴘᴀᴍ, ᴏʀ ʏᴏᴜ'ʟʟ ɢᴇᴛ ʙʟᴏᴄᴋᴇᴅ ᴀɴᴅ ʀᴇᴘᴏʀᴛᴇᴅ ʙʏ ᴍᴇ.**"
)
BLOCKED = "**ʙᴇᴇᴘ ʙᴏᴏᴘ ꜰᴏᴜɴᴅᴇᴅ ᴀ ꜱᴘᴀᴍᴍᴇʀ!, ʙʟᴏᴄᴋᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!**"
LIMIT = 5


async def set_pm(value: bool):
    await collection.update_one(
        {"_id": 1},
        {"$set": {"pmpermit": bool(value)}},
        upsert=True,
    )
    await collection.update_one(
        {"_id": "Approved"},
        {"$setOnInsert": {"users": []}},
        upsert=True,
    )


async def set_permit_message(text):
    await collection.update_one(
        {"_id": 1}, {"$set": {"pmpermit_message": text}}, upsert=True
    )


async def set_block_message(text):
    await collection.update_one(
        {"_id": 1}, {"$set": {"block_message": text}}, upsert=True
    )


async def set_limit(limit):
    await collection.update_one(
        {"_id": 1}, {"$set": {"limit": max(1, int(limit))}}, upsert=True
    )


async def get_pm_settings():
    result = await collection.find_one({"_id": 1})
    if not result:
        return False, PMPERMIT_MESSAGE, LIMIT, BLOCKED
    return (
        bool(result.get("pmpermit", False)),
        result.get("pmpermit_message", PMPERMIT_MESSAGE),
        int(result.get("limit", LIMIT)),
        result.get("block_message", BLOCKED),
    )


async def allow_user(chat):
    await collection.update_one(
        {"_id": "Approved"},
        {"$addToSet": {"users": chat}},
        upsert=True,
    )


async def get_approved_users():
    result = await collection.find_one({"_id": "Approved"})
    return result.get("users", []) if result else []


async def deny_user(chat):
    await collection.update_one(
        {"_id": "Approved"},
        {"$pull": {"users": chat}},
        upsert=True,
    )


async def pm_guard():
    result = await collection.find_one({"_id": 1})
    return bool(result and result.get("pmpermit", False))
