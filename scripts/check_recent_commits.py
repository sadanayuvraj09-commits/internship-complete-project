import bootstrap
from src.database import db
import asyncio


async def main():
    total = await db["activity_logs"].count_documents({"source": "github"})
    print(f"Total github docs: {total}")

    # Which repos/owners does this data actually belong to?
    distinct_repos = await db["activity_logs"].distinct("project", {"source": "github"})
    distinct_owners = await db["activity_logs"].distinct("repo_owner", {"source": "github"})
    print(f"\nDistinct 'project' (repo_name) values: {distinct_repos}")
    print(f"Distinct 'repo_owner' values: {distinct_owners}")

    # Count per repo
    for repo in distinct_repos:
        c = await db["activity_logs"].count_documents({"source": "github", "project": repo})
        print(f"  {repo}: {c} commits")


asyncio.run(main())