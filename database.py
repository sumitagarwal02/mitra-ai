import sqlite3

DB_NAME = "checkins.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            prompt TEXT,
            mood_analysis TEXT,
            micro_exercise TEXT,
            journal_prompt TEXT,
            youtube_search_query TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_checkin(user_id: str, prompt: str, rec):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO checkins (user_id, prompt, mood_analysis, micro_exercise, journal_prompt, youtube_search_query)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, prompt, rec.mood_analysis, rec.micro_exercise, rec.journal_prompt, rec.youtube_search_query))
    conn.commit()
    conn.close()

def fetch_history(user_id: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if user_id:
        cursor.execute("""
            SELECT timestamp, prompt, mood_analysis, micro_exercise, journal_prompt, youtube_search_query 
            FROM checkins 
            WHERE user_id = ?
            ORDER BY timestamp DESC
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT timestamp, prompt, mood_analysis, micro_exercise, journal_prompt, youtube_search_query 
            FROM checkins 
            ORDER BY timestamp DESC
        """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_total_count(user_id: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT COUNT(*) FROM checkins WHERE user_id = ?", (user_id,))
    else:
        cursor.execute("SELECT COUNT(*) FROM checkins")
    row = cursor.fetchone()
    count = row[0] if row else 0
    conn.close()
    return count