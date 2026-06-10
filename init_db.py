"""
Creates the SQLite schema for the Analects catalogue
Stores in analects.db
"""

import sqlite3

### CONSTANTS
DB_PATH = "analects.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Drop existing tables (for clean re-runs)
    # Full Text Search - the search index table lives alongside passages
    # AI - After Insert
    # AU - After Update
    # AD - After Delete

    cur.executescript("""
        DROP TABLE IF EXISTS passages_fts;
        DROP TRIGGER IF EXISTS passages_ai;
        DROP TRIGGER IF EXISTS passages_au;
        DROP TRIGGER IF EXISTS passages_ad;
        DROP TABLE IF EXISTS tags;
        DROP TABLE IF EXISTS passages;
    """)

    # Main Table
    cur.execute("""
        CREATE TABLE passages (
            id      TEXT PRIMARY KEY,        -- "1.10"
            book    INTEGER NOT NULL,
            chapter INTEGER NOT NULL,
            text    TEXT NOT NULL,
            starred INTEGER NOT NULL DEFAULT 0,
            note    TEXT NOT NULL DEFAULT ''
        );
    """)

    # Tags - one row per (passage, tag) tuple pair
    cur.execute("""
        CREATE TABLE tags (
            passage_id  TEXT NOT NULL,
            tag         TEXT NOT NULL,
            PRIMARY KEY (passage_id, tag),
            FOREIGN KEY (passage_id) REFERENCES passages(id) ON DELETE CASCADE
        );
    """)

    # Create an index
    cur.execute("CREATE INDEX idx_tags_tag ON tags(tag);")

    # Virtuable table with tokenization proper for chinese
    cur.execute("""
        CREATE VIRTUAL TABLE passages_fts USING fts5(
            id UNINDEXED,
            text,
            tokenize = "unicode61 categories 'L* N* Co'"
        );
    """)

    # Create the triggers to keep passage_fts in sync with passages
    cur.executescript("""
        CREATE TRIGGER passages_ai AFTER INSERT ON passages BEGIN
            INSERT INTO passages_fts (id, text) VALUES (new.id, new.text);
        END;
        CREATE TRIGGER passages_au AFTER UPDATE ON passages BEGIN
            UPDATE passages_fts SET text = new.text WHERE id = new.id;
        END;
        CREATE TRIGGER passages_ad AFTER DELETE ON passages BEGIN
            DELETE FROM passages_fts WHERE id = old.id;
        END;
    """)

    conn.commit()
    conn.close()
    print(f"Initialized fresh database at {DB_PATH}")

if __name__ == "__main__":
    init_db()
