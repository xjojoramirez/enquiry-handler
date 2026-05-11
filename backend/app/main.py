from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import get_pool, close_pool
from app.db.migrations import run_migrations
from app.routers.enquiries import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool = await get_pool()
    await run_migrations(pool)
    yield
    await close_pool()


app = FastAPI(title="AI Enquiry Handler", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
