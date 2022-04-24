from app.services.workers import get_registered


async def get_users(**kwargs):
    return {
        "users": await get_registered(),
    }
