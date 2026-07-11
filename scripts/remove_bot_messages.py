import bootstrap
from src.database import db
import asyncio


async def main():
    result = await db["activity_logs"].delete_many({"developer_id": "B0BEQG73GAD"})
    print(f"Deleted {result.deleted_count} bot-authored messages")


asyncio.run(main())