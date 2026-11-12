# backend/database.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'data', 'raw')
DB_PATH = os.path.join(DB_DIR, 'experiment.db')

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_id          TEXT PRIMARY KEY,
            participant_id    TEXT NOT NULL,
            session_id        TEXT NOT NULL,
            condition         TEXT NOT NULL,
            condition_order   TEXT NOT NULL,
            task_id           TEXT,
            event_type        TEXT NOT NULL,
            element_id        TEXT,
            timestamp         TEXT NOT NULL,
            server_timestamp  TEXT NOT NULL,
            elapsed_ms        REAL,
            x                 REAL,
            y                 REAL,
            metadata          TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_event(event_dict):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO events (
                event_id, participant_id, session_id, condition, condition_order,
                task_id, event_type, element_id, timestamp, server_timestamp,
                elapsed_ms, x, y, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            event_dict['event_id'],
            event_dict['participant_id'],
            event_dict['session_id'],
            event_dict['condition'],
            event_dict['condition_order'],
            event_dict.get('task_id'),
            event_dict['event_type'],
            event_dict.get('element_id'),
            event_dict['timestamp'],
            event_dict['server_timestamp'],
            event_dict.get('elapsed_ms'),
            event_dict.get('x'),
            event_dict.get('y'),
            event_dict.get('metadata')
        ))
        conn.commit()
    except sqlite3.Error as e:
        conn.close()
        raise e
    finally:
        conn.close()

def get_event_count():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM events")
    count = cursor.fetchone()[0]
    conn.close()
    return count
