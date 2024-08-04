import sqlite3
from pathlib import Path

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.static_files import create_static_files_router
from litestar.template.config import TemplateConfig

__all__ = [
    "static_router",
    "template_config",
    "create_database",
]

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
TEMPLATE_DIR = Path(__file__).resolve().parents[2] / "templates"

DATABASE_PATH = Path(__file__).resolve().parents[2] / "fileDB.db"

static_router = create_static_files_router("/static", [STATIC_DIR])
template_config = TemplateConfig(
    engine=JinjaTemplateEngine,
    directory=TEMPLATE_DIR,
)


def create_database() -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS file (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            link TEXT
        )
        """,
    )
    return connection, cursor
