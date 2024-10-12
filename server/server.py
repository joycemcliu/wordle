import logging
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from middleware.custom_logging import logger_config, setup_logging
from models.migration import run_migrations
from models.session import init_db_session, sessionmanager
from views import game

setup_logging()
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)


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
app.include_router(game.router, prefix="/v1")


@app.get("/health")
async def health():
    return


if __name__ == "__main__":
    realod = os.environ.get("ENV", "dev") == "dev"
    uvicorn.run("server:app", host="0.0.0.0", port=8010, reload=realod, log_config=logger_config)
