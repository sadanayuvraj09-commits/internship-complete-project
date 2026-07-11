import bootstrap
from src.database import db
from pymongo.errors import DuplicateKeyError
import asyncio


async def main():
    slack_ids_to_merge = ["U0BEK7GFCCD", "U0BELELC71U"]
    canonical_id = "YUVRAJ SADANA"

    for collection_name in ["activity_logs", "detected_gaps", "timesheet_entries"]:
        coll = db[collection_name]
        for old_id in slack_ids_to_merge:
            docs = await coll.find({"developer_id": old_id}).to_list(10000)
            updated = 0
            deleted_dupes = 0

            for doc in docs:
                try:
                    await coll.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {"developer_id": canonical_id}}
                    )
                    updated += 1
                except DuplicateKeyError:
                    await coll.delete_one({"_id": doc["_id"]})
                    deleted_dupes += 1

            print(f"{collection_name}: {old_id} -> {canonical_id} "
                  f"({updated} updated, {deleted_dupes} duplicates removed)")


asyncio.run(main())