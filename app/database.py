from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from app.configure import settings
import asyncio
import os

load_dotenv()

'''PORT = os.getenv("PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

MONGO_URI = f"mongodb://{DB_USER}:{DB_PASSWORD}@localhost:{PORT}/{DB_NAME}?authSource=admin"'''

client = AsyncIOMotorClient(settings.MONGO_URI)
db = client[settings.DB_NAME]

async def test_connection():
    try: 
        await client.admin.command("ping")
        print("Connected to MongoDB successfully!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
