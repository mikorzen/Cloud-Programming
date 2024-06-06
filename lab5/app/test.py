import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parents[1] / "fileDB.db"

connection = sqlite3.connect(DATABASE_PATH)
cursor = connection.cursor()


def create_database() -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS file (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            link TEXT
        )
        """,
    )


if __name__ == "__main__":
    create_database()
    cursor.execute(
        "INSERT INTO file (name, link) VALUES (?, ?)",
        ("ooo", "aaa"),
    )
    connection.commit()
