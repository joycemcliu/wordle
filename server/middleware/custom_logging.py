# logging config for uvicorn into console and rotating log file in logs folder
from pathlib import Path


def setup_logging() -> None:
    Path("logs").mkdir(exist_ok=True)


logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(name)s - %(levelprefix)s %(message)s",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
        "file": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "file",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs/wordleserver.log",
            "when": "D",
            "backupCount": 10,
            "encoding": "utf8",
        },
        "error": {
            "formatter": "file",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "logs/wordleserver-error.log",
            "when": "D",
            "backupCount": 10,
            "encoding": "utf8",
        },
    },
    "loggers": {
        "root": {"handlers": ["default", "file"], "level": "DEBUG", "propagate": False},
        # "uvicorn": {
        #     "handlers": ["default", "file"],
        #     "level": "DEBUG",
        #     "propagate": False,
        # },
        # "uvicorn.access": {
        #     "handlers": ["access", "file"],
        #     "level": "DEBUG",
        #     "propagate": False,
        # },
        # "uvicorn.asgi": {
        #     "handlers": ["default", "file"],
        #     "level": "DEBUG",
        #     "propagate": False,
        # },
        "uvicorn.error": {
            "handlers": ["error"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
