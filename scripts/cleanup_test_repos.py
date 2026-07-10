import bootstrap
from src.database import db
import asyncio


async def main():
    repos_to_remove = ["flask", "linux", "revenue_detective_test"]

    for repo in repos_to_remove:
        result = await db["activity_logs"].delete_many({"source": "github", "project": repo})
        print(f"Deleted {result.deleted_count} docs for project '{repo}'")

    remaining = await db["activity_logs"].count_documents({"source": "github"})
    print(f"\nRemaining github docs: {remaining}")


asyncio.run(main())