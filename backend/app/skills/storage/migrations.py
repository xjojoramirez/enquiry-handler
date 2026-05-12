import asyncpg


async def run_migrations(pool: asyncpg.Pool):
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS enquiries (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                original_text TEXT NOT NULL,
                classification JSONB NOT NULL,
                priority VARCHAR(20) NOT NULL DEFAULT 'medium',
                summary TEXT,
                entities JSONB DEFAULT '{}',
                recommended_team VARCHAR(100),
                suggested_response TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_enquiries_created_at
            ON enquiries (created_at DESC);
        """)
