"""Simple SQLite database for card caching."""
import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "cards.db"


def get_connection() -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            series TEXT,
            release_date TEXT,
            regulation_mark TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            card_type TEXT NOT NULL,
            subtype TEXT,
            set_code TEXT NOT NULL,
            set_number TEXT,
            regulation_mark TEXT,
            hp INTEGER,
            energy_type TEXT,
            abilities TEXT,
            attacks TEXT,
            image_url TEXT,
            UNIQUE(set_code, set_number)
        )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_regulation ON cards(regulation_mark)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(card_type)")

    conn.commit()
    conn.close()


def get_card(set_code: str, set_number: str) -> Optional[dict]:
    """Get card by set code and number."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM cards WHERE set_code = ? AND set_number = ?",
        (set_code.upper(), set_number)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_card_by_name(name: str) -> Optional[dict]:
    """Get card by exact name."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_card(card: dict):
    """Save or update a card."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO cards
        (name, card_type, subtype, set_code, set_number, regulation_mark,
         hp, energy_type, abilities, attacks, image_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        card.get("name"),
        card.get("card_type"),
        card.get("subtype"),
        card.get("set_code"),
        card.get("set_number"),
        card.get("regulation_mark"),
        card.get("hp"),
        card.get("energy_type"),
        card.get("abilities"),
        card.get("attacks"),
        card.get("image_url")
    ))
    conn.commit()
    conn.close()


def get_cards_by_regulation(regulation_mark: str) -> list[dict]:
    """Get all cards with a specific regulation mark."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM cards WHERE regulation_mark = ?",
        (regulation_mark,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_cards_by_set(set_code: str) -> list[dict]:
    """Get all cards from a set."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM cards WHERE set_code = ?",
        (set_code.upper(),)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_cards_by_type_and_subtype(card_type: str, subtype: str = None) -> list[dict]:
    """Get cards by type and optionally subtype."""
    conn = get_connection()
    cursor = conn.cursor()
    if subtype:
        cursor.execute(
            "SELECT * FROM cards WHERE card_type = ? AND subtype = ? AND regulation_mark != 'G'",
            (card_type, subtype)
        )
    else:
        cursor.execute(
            "SELECT * FROM cards WHERE card_type = ? AND regulation_mark != 'G'",
            (card_type,)
        )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
