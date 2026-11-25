# database.py
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "coshh_database.db"

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            chemical TEXT,
            assessor TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            payload TEXT NOT NULL
        )
    """)
    con.commit()
    return con

def save_assessment(data, assessment_id=None):
    now = datetime.now().isoformat(timespec="minutes")
    con = connect()
    payload = json.dumps(data, ensure_ascii=False)
    if assessment_id:
        con.execute("""UPDATE assessments SET title=?, chemical=?, assessor=?,
                    updated_at=?, payload=? WHERE id=?""",
                    (data.get("title", "بدون عنوان"), data.get("chemical", ""),
                     data.get("assessor", ""), now, payload, assessment_id))
        aid = assessment_id
    else:
        cur = con.execute("""INSERT INTO assessments
            (title, chemical, assessor, created_at, updated_at, payload)
            VALUES (?,?,?,?,?,?)""",
            (data.get("title", "بدون عنوان"), data.get("chemical", ""),
             data.get("assessor", ""), now, now, payload))
        aid = cur.lastrowid
    con.commit()
    con.close()
    return aid

def list_assessments(search=""):
    con = connect()
    q = f"%{search}%"
    rows = con.execute("""SELECT id, title, chemical, assessor, updated_at
        FROM assessments WHERE title LIKE ? OR chemical LIKE ?
        ORDER BY updated_at DESC""", (q, q)).fetchall()
    con.close()
    return [dict(r) for r in rows]

def get_assessment(aid):
    con = connect()
    row = con.execute("SELECT * FROM assessments WHERE id=?", (aid,)).fetchone()
    con.close()
    if not row:
        return None
    result = dict(row)
    result["payload"] = json.loads(result["payload"])
    return result

def delete_assessment(aid):
    con = connect()
    con.execute("DELETE FROM assessments WHERE id=?", (aid,))
    con.commit()
    con.close()