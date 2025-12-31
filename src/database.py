# src/database.py
import sqlite3
import json

DB_NAME = "history.db"

def init_db():
    """Creates the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS runs
                 (start_page TEXT, target_page TEXT, path_json TEXT, clicks INTEGER)''')
    conn.commit()
    conn.close()

def save_run(start, target, path):
    """Saves a successful run."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Check if exists first
    c.execute("SELECT * FROM runs WHERE start_page=? AND target_page=?", (start, target))
    if not c.fetchone():
        c.execute("INSERT INTO runs VALUES (?, ?, ?, ?)", 
                  (start, target, json.dumps(path), len(path)-1))
        conn.commit()
    conn.close()

def check_memory(start, target):
    """Returns the path if we have solved this before."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT path_json FROM runs WHERE start_page=? AND target_page=?", (start, target))
    result = c.fetchone()
    conn.close()
    if result:
        return json.loads(result[0])
    return None
    