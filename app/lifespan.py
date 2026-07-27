from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    # print("Starting up...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # print("Shutting down...")
    await engine.dispose()