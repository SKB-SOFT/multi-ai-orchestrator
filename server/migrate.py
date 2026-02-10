import sqlite3
import os
from pathlib import Path

def migrate():
    # Attempt to find the database path
    # The default in .env is sqlite+aiosqlite:///../data/app.db (relative to server/) or similar
    # In db.py it defaults to ../data/app.db relative to server/
    
    db_paths = [
        "data/app.db",
        "../data/app.db",
        "server/data/app.db",
        "app.db"
    ]
    
    found_path = None
    for p in db_paths:
        if os.path.exists(p):
            found_path = p
            break
            
    if not found_path:
        print("Could not find app.db automatically. Please check your DATABASE_URL.")
        return

    print(f"Found database at: {found_path}")
    conn = sqlite3.connect(found_path)
    cursor = conn.cursor()

    try:
        print("Adding 'consent_research' column to 'users' table...")
        cursor.execute("ALTER TABLE users ADD COLUMN consent_research BOOLEAN DEFAULT 1")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("'consent_research' already exists.")
        else:
            print(f"Error adding 'consent_research': {e}")

    try:
        print("Adding 'anonymize_data' column to 'users' table...")
        cursor.execute("ALTER TABLE users ADD COLUMN anonymize_data BOOLEAN DEFAULT 0")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("'anonymize_data' already exists.")
        else:
            print(f"Error adding 'anonymize_data': {e}")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate()
