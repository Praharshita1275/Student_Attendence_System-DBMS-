import sqlite3
from pathlib import Path

def init_db():
    db_path = Path('attendance_system.db')
    if db_path.exists():
        db_path.unlink()  # Remove existing database
        
    # Read schema.sql and execute its commands
    with open('schema.sql') as f:
        schema = f.read()
    
    with sqlite3.connect('attendance_system.db') as conn:
        conn.executescript(schema)
        print("Database initialized successfully with views")
        
if __name__ == '__main__':
    init_db()
