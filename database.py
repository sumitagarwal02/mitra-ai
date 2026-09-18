import sqlite3
from datetime import datetime

DB_NAME = "mitra.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_input TEXT,
            mood_analysis TEXT,
            micro_exercise TEXT,
            journal_prompt TEXT,
            youtube_query TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_checkin(user_input, rec):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO checkins (timestamp, user_input, mood_analysis, micro_exercise, journal_prompt, youtube_query)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        user_input,
        rec.mood_analysis,
        rec.micro_exercise,
        rec.journal_prompt,
        rec.youtube_search_query
    ))
    conn.commit()
    conn.close()

def fetch_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, user_input, mood_analysis, micro_exercise, journal_prompt, youtube_query 
        FROM checkins ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_total_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM checkins")
    count = cursor.fetchone()[0]
    conn.close()
    return count