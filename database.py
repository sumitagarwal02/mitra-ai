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
            youtube_search_query TEXT,
            stress_level INTEGER DEFAULT 5,
            energy_level INTEGER DEFAULT 5,
            dominant_emotion TEXT DEFAULT 'Neutral'
        )
    """)
    
    # Automatic schema migration for existing database files
    cursor.execute("PRAGMA table_info(checkins)")
    existing_cols = [column[1] for column in cursor.fetchall()]
    
    if "stress_level" not in existing_cols:
        cursor.execute("ALTER TABLE checkins ADD COLUMN stress_level INTEGER DEFAULT 5")
    if "energy_level" not in existing_cols:
        cursor.execute("ALTER TABLE checkins ADD COLUMN energy_level INTEGER DEFAULT 5")
    if "dominant_emotion" not in existing_cols:
        cursor.execute("ALTER TABLE checkins ADD COLUMN dominant_emotion TEXT DEFAULT 'Neutral'")

    conn.commit()
    conn.close()

def save_checkin(user_id: str, prompt: str, rec):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO checkins (
            user_id, prompt, mood_analysis, micro_exercise, 
            journal_prompt, youtube_search_query, stress_level, 
            energy_level, dominant_emotion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, 
        prompt, 
        rec.mood_analysis, 
        rec.micro_exercise, 
        rec.journal_prompt, 
        rec.youtube_search_query,
        getattr(rec, 'stress_level', 5),
        getattr(rec, 'energy_level', 5),
        getattr(rec, 'dominant_emotion', 'Neutral')
    ))
    conn.commit()
    conn.close()

def fetch_history(user_id: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if user_id:
        cursor.execute("""
            SELECT timestamp, prompt, mood_analysis, micro_exercise, 
                   journal_prompt, youtube_search_query, stress_level, 
                   energy_level, dominant_emotion 
            FROM checkins 
            WHERE user_id = ?
            ORDER BY timestamp DESC
        """, (user_id,))
    else:
        cursor.execute("""
            SELECT timestamp, prompt, mood_analysis, micro_exercise, 
                   journal_prompt, youtube_search_query, stress_level, 
                   energy_level, dominant_emotion 
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