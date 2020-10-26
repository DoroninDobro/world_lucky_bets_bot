import asyncio
from app.models.db import generate_schemas_db


async def main():
    await generate_schemas_db()

if __name__ == "__main__":
    asyncio.run(main())
