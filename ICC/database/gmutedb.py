from ICC.database import cli

gmuteh = cli["GMUTE"]


async def is_gmuted(sender_id):
    return await gmuteh.find_one({"sender_id": sender_id}) is not None


async def gmute(sender_id, reason="#GMuted"):
    await gmuteh.update_one(
        {"sender_id": sender_id},
        {"$set": {"reason": reason}},
        upsert=True,
    )


async def ungmute(sender_id):
    await gmuteh.delete_one({"sender_id": sender_id})
