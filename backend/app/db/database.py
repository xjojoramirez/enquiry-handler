import asyncpg
from app.config.settings import settings

pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global pool
    if pool is None:
        dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
        pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
    return pool


async def close_pool():
    global pool
    if pool:
        await pool.close()
        pool = None
