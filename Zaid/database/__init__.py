import motor.motor_asyncio

from config import MONGO_URL

if not MONGO_URL:
    raise RuntimeError("MONGO_URL is missing. Configure your MongoDB connection string.")

cli = motor.motor_asyncio.AsyncIOMotorClient(
    MONGO_URL,
    serverSelectionTimeoutMS=10000,
)
dbb = cli.program
