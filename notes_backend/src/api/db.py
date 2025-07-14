import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional

from .models import NoteCreate, NoteInDB, NoteUpdate

DB_PATH = os.getenv("NOTES_DB_PATH", "notes.db")

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_tables():
    with get_db() as db:
        db.execute(
            '''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            '''
        )
        db.commit()


# PUBLIC_INTERFACE
def db_create_note(note: NoteCreate) -> NoteInDB:
    now = datetime.utcnow().isoformat()
    with get_db() as db:
        cursor = db.execute(
            'INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)',
            (note.title, note.content, now, now)
        )
        db.commit()
        note_id = cursor.lastrowid
        return db_get_note(note_id)


# PUBLIC_INTERFACE
def db_get_notes() -> List[NoteInDB]:
    with get_db() as db:
        rows = db.execute('SELECT * FROM notes ORDER BY created_at DESC').fetchall()
        return [db_row_to_note(row) for row in rows]


# PUBLIC_INTERFACE
def db_get_note(note_id: int) -> Optional[NoteInDB]:
    with get_db() as db:
        row = db.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
        return db_row_to_note(row) if row else None


# PUBLIC_INTERFACE
def db_update_note(note_id: int, note: NoteUpdate) -> Optional[NoteInDB]:
    with get_db() as db:
        current_note = db.execute('SELECT * FROM notes WHERE id = ?', (note_id,)).fetchone()
        if not current_note:
            return None
        updated_title = note.title if note.title is not None else current_note["title"]
        updated_content = note.content if note.content is not None else current_note["content"]
        now = datetime.utcnow().isoformat()
        db.execute(
            'UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?',
            (updated_title, updated_content, now, note_id)
        )
        db.commit()
        return db_get_note(note_id)


# PUBLIC_INTERFACE
def db_delete_note(note_id: int) -> bool:
    with get_db() as db:
        cursor = db.execute('DELETE FROM notes WHERE id = ?', (note_id,))
        db.commit()
        return cursor.rowcount > 0


def db_row_to_note(row: sqlite3.Row) -> NoteInDB:
    return NoteInDB(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


# Run table creation on module import
create_tables()
