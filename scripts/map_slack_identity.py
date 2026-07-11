import bootstrap
from src.database import db
import asyncio


async def main():
    result = await db["developers"].update_one(
        {"developer_id": "YUVRAJ SADANA"},
        {
            "$set": {
                "developer_id": "YUVRAJ SADANA",
                "slack_user_id": "U0BEK7GFCCD",
            },
            "$addToSet": {
                "slack_user_ids": {"$each": ["U0BEK7GFCCD", "U0BELELC71U"]}
            },
        },
        upsert=True,
    )
    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted: {result.upserted_id}")


asyncio.run(main())