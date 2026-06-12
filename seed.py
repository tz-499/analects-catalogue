# seed.py

"""
Fetches the Analects from ctext.org in simplified Chinese
Loaded into the SQLite database created by init_db.py
"""

import sqlite3
from ctext import setapikey, setremap, gettextasparagrapharray

DB_PATH = "analects.db"

# The 20 books of the Analects, in order.
# Each tuple is (book_number, urn_suffix).
BOOKS = [
    (1,  "xue-er"),
    (2,  "wei-zheng"),
    (3,  "ba-yi"),
    (4,  "li-ren"),
    (5,  "gong-ye-chang"),
    (6,  "yong-ye"),
    (7,  "shu-er"),
    (8,  "tai-bo"),
    (9,  "zi-han"),
    (10, "xiang-dang"),
    (11, "xian-jin"),
    (12, "yan-yuan"),
    (13, "zi-lu"),
    (14, "xian-wen"),
    (15, "wei-ling-gong"),
    (16, "ji-shi"),
    (17, "yang-huo"),
    (18, "wei-zi"),
    (19, "zi-zhang"),
    (20, "yao-yue"),
]

def seed():
    # Configure ctext API for Simplified Chinese output
    setapikey("demo")
    setremap("gb")

    # db connector
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    total_inserted = 0

    for book_num, urn_suffix in BOOKS:
        urn = f"ctp:analects/{urn_suffix}"
        print(f"Fetching Book {book_num}: {urn}...", end=" ")

        passages = gettextasparagrapharray(urn)

        for chapter_num, text in enumerate(passages, start=1):
            passage_id = f"{book_num}.{chapter_num}"
            cur.execute(
                "INSERT INTO passages (id, book, chapter, text) VALUES (?, ?, ?, ?)",
                (passage_id, book_num, chapter_num, text),
            )
            total_inserted += 1

        print(f"{len(passages)} passages")

    conn.commit()
    conn.close()
    print(f"\nDone - {total_inserted} passages loaded into database")

if __name__ == "__main__":
    seed()
