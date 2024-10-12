import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from models.migration import run_migrations
from models.session import init_db_session, sessionmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    url = os.environ.get("POSTGRES_URL")
    run_migrations(url)
    init_db_session(url.replace("postgresql", "postgresql+asyncpg"))

    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def home():
    return "hello world"


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
