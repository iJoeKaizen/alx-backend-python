import asyncio
import aiosqlite

async def async_fetch_users():
    """Fetch all users from the database"""
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall()
            print("All users fetched:")
            for row in results:
                print(row)
            return results

async def async_fetch_older_users():
    """Fetch users older than 40"""
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            results = await cursor.fetchall()
            print("\nUsers older than 40 fetched:")
            for row in results:
                print(row)
            return results

async def fetch_concurrently():
    """Run both queries concurrently"""
    return await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )

# Run the concurrent queries
if __name__ == "__main__":
    results = asyncio.run(fetch_concurrently())
    print("\nFinal results:")
    print("All users:", results[0])
    print("Users > 40:", results[1])