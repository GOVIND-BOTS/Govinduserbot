from Zaid.database import cli

collection = cli["Zaid"]["rraid"]


async def rraid_user(chat):
    await collection.update_one(
        {"_id": "Rraid"},
        {"$addToSet": {"users": chat}},
        upsert=True,
    )


async def get_rraid_users():
    result = await collection.find_one({"_id": "Rraid"})
    return result.get("users", []) if result else []


async def unrraid_user(chat):
    await collection.update_one(
        {"_id": "Rraid"},
        {"$pull": {"users": chat}},
        upsert=True,
    )
