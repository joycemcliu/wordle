import os

ENV = os.environ.get("ENV", "dev")
DB_URL = os.environ.get("POSTGRES_URL")
DEFAULT_MAX_ATTEMPTS = os.environ.get("MAX_ATTEMPTS", 6)
DEFAULT_LEN_WORD = os.environ.get("LEN_WORD", 5)

DEFAULT_WORD_LIST = os.environ.get("WORD_LIST")
if DEFAULT_WORD_LIST:
    DEFAULT_WORD_LIST = DEFAULT_WORD_LIST.split(",")
else:
    DEFAULT_WORD_LIST = [
        "hello",
        "world",
        "quite",
        "fancy",
        "fresh",
        "panic",
        "crazy",
        "buggy",
        "scare",
    ]
