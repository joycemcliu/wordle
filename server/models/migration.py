from pathlib import Path

from alembic import command
from alembic.config import Config


def run_migrations(dsn: str) -> None:
    # parse url redact password
    redacted = dsn.replace(dsn.split("@")[0].split("://")[1], "********")
    script_location = Path(__file__).resolve().parent.parent / "alembic"
    print(f"Running DB migrations in {script_location} on {redacted}")
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", script_location.as_posix())
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        print(f"Error running migrations: {e}")
        exit(1)
