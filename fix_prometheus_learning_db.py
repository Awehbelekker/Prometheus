"""Fix prometheus_learning.db - add missing tables and columns"""
import sqlite3

def main():
    db_path = 'prometheus_learning.db'
    print(f"Checking {db_path}...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get existing tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Existing tables: {tables}")

    # Create open_positions table if missing
    if 'open_positions' not in tables:
        print("Creating open_positions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS open_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                unrealized_pl REAL DEFAULT 0,
                broker TEXT NOT NULL,
                opened_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(symbol, broker)
            )
        """)
        conn.commit()
        print("open_positions table created!")
    else:
        print("open_positions table already exists")

    # Check and add ai_confidence column to trade_history if missing
    if 'trade_history' in tables:
        cursor.execute("PRAGMA table_info(trade_history)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"trade_history columns: {columns}")

        if 'ai_confidence' not in columns:
            print("Adding ai_confidence column to trade_history...")
            cursor.execute("ALTER TABLE trade_history ADD COLUMN ai_confidence REAL DEFAULT 0")
            conn.commit()
            print("ai_confidence column added!")
        else:
            print("ai_confidence column already exists")

    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()

