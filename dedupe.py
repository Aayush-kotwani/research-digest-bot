import sqlite3
import os
from contextlib import closing

DB_PATH = os.path.join(os.path.dirname(__file__), 'seen.db')

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS seen_items (
                    id TEXT PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()

def is_seen(item_id: str) -> bool:
    if not os.path.exists(DB_PATH):
        init_db()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('SELECT 1 FROM seen_items WHERE id = ?', (item_id,))
            return cursor.fetchone() is not None

def mark_seen(item_id: str):
    if not os.path.exists(DB_PATH):
        init_db()
    with closing(sqlite3.connect(DB_PATH)) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('INSERT OR IGNORE INTO seen_items (id) VALUES (?)', (item_id,))
        conn.commit()

if __name__ == "__main__":
    init_db()
