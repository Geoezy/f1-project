import sqlite3
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Check instance folder first
if os.path.exists(os.path.join(BASE_DIR, 'instance', 'f1_2026.db')):
    DB_PATH = os.path.join(BASE_DIR, 'instance', 'f1_2026.db')
else:
    DB_PATH = os.path.join(BASE_DIR, 'f1_2026.db')
print(f"Using DB at: {DB_PATH}")

def run_migration():
    print("Migrating Database Schema...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Existing tables: {tables}")
    
    # Driver Columns
    driver_cols = [
        ("country_code", "TEXT"),
        ("podiums", "INTEGER DEFAULT 0"),
        ("world_championships", "INTEGER DEFAULT 0"),
        ("highest_finish", "TEXT DEFAULT 'N/A'"),
        ("biography", "TEXT"),
        ("image_url", "TEXT")
    ]

    driver_table = "driver" if "driver" in tables else "Driver"
    cursor.execute(f"PRAGMA table_info({driver_table})")
    current_cols = [row[1] for row in cursor.fetchall()]
    
    for col_name, col_type in driver_cols:
        if col_name not in current_cols:
            print(f"Adding {col_name} to {driver_table}...")
            try:
                cursor.execute(f"ALTER TABLE {driver_table} ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")

    # Constructor Columns
    # Constructor Columns
    constructor_cols = [
        ("base", "TEXT"),
        ("team_principal", "TEXT"),
        ("car_image_url", "TEXT"),
        ("sponsors", "TEXT"),
        ("world_championships", "INTEGER DEFAULT 0"),
        ("highest_finish", "TEXT DEFAULT 'N/A'")
    ]

    const_table = "constructor" if "constructor" in tables else "Constructor"
    cursor.execute(f"PRAGMA table_info({const_table})")
    current_cols = [row[1] for row in cursor.fetchall()]
    
    for col_name, col_type in constructor_cols:
        if col_name not in current_cols:
            print(f"Adding {col_name} to {const_table}...")
            try:
                cursor.execute(f"ALTER TABLE {const_table} ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")

    conn.commit()
    conn.close()
    print("Migration Complete.")

if __name__ == "__main__":
    run_migration()
