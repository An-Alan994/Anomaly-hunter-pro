import sqlite3
from contextlib import contextmanager
from utils.config import Config

class DatabaseManager:
    def __init__(self):
        self.db_name = Config.DB_PATH
        self._init_db()

    def _init_db(self):
        with self.get_connection() as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT,
                side TEXT,
                price REAL,
                size REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )""")

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
