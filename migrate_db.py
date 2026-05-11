import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'esctrix.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path, timeout=10)
    cursor = conn.cursor()
    
    # Try adding role column (will fail if already exists, which is fine)
    try:
        cursor.execute("ALTER TABLE user ADD COLUMN role VARCHAR(20) DEFAULT 'candidate'")
        print("Added 'role' column to 'user' table.")
    except sqlite3.OperationalError as e:
        print(f"Role column might already exist: {e}")

    # Create ATSCheck table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ats_check (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        job_description TEXT,
        resume_filename VARCHAR(200),
        score INTEGER,
        result_data TEXT,
        FOREIGN KEY(user_id) REFERENCES user(id)
    )
    """)
    print("Created 'ats_check' table.")
    
    conn.commit()
    conn.close()
    print("Migration completed successfully.")
except Exception as e:
    print(f"Migration error: {e}")
