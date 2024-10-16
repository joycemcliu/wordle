import logging
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from config import DB_URL, ENV
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
    try:
        run_migrations(DB_URL)
        init_db_session(DB_URL.replace("postgresql", "postgresql+asyncpg"))
    except Exception as e:
        logger.error(f"Error connecting to DB: {e}")
        sys.exit(1)
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


app = FastAPI(lifespan=lifespan)
client_port = os.environ.get("CLIENT_PORT")
origins = [
    f"http://localhost:{client_port}",
    f"http://127.0.0.1:{client_port}",
    f"http://0.0.0.0:{client_port}",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return


app.include_router(game.router, prefix="/v1", tags=["game"])


if __name__ == "__main__":
    realod = ENV == "dev"
    uvicorn.run("server:app", host="0.0.0.0", port=8010, reload=realod, log_config=logger_config)
