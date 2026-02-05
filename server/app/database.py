import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager

DB_PATH = "brain.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS brain_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            answer TEXT,
            confidence REAL,
            brain_strength REAL DEFAULT 0.0,
            response_time REAL,
            providers_used TEXT,
            success BOOLEAN,
            user_feedback INTEGER,
            request_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS error_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT,
            endpoint TEXT,
            error TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def log_response(query: str, answer: str, confidence: float, brain_strength: float, response_time: float, providers_used: list, success: bool, request_id: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO brain_responses 
        (query, answer, confidence, brain_strength, response_time, providers_used, success, request_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (query, answer, confidence, brain_strength, response_time, json.dumps(providers_used), success, request_id))
    response_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return response_id

def log_error(request_id: str, endpoint: str, error: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO error_logs (request_id, endpoint, error) VALUES (?, ?, ?)', (request_id, endpoint, error))
    conn.commit()
    conn.close()

def set_user_feedback(response_id: int, feedback: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE brain_responses SET user_feedback = ? WHERE id = ?', (feedback, response_id))
    conn.commit()
    conn.close()
