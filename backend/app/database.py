
"""Local SQLite storage with configurable persistent data directory."""

import sqlite3
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR)))

DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "question_papers.db"


def connect():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with connect() as c:
        c.execute(
            "CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY,data TEXT NOT NULL)"
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS papers(id TEXT PRIMARY KEY,data TEXT NOT NULL,created_at TEXT NOT NULL)"
        )


def save_document(i, d):
    with connect() as c:
        c.execute(
            "INSERT OR REPLACE INTO documents VALUES(?,?)",
            (i, json.dumps(d, ensure_ascii=False))
        )


def get_document(i):
    with connect() as c:
        r = c.execute(
            "SELECT data FROM documents WHERE id=?", (i,)
        ).fetchone()
        return json.loads(r["data"]) if r else None


def save_paper(i, d):
    with connect() as c:
        c.execute(
            "INSERT OR REPLACE INTO papers VALUES(?,?,?)",
            (i, json.dumps(d, ensure_ascii=False), d["created_at"])
        )


def get_paper(i):
    with connect() as c:
        r = c.execute(
            "SELECT data FROM papers WHERE id=?", (i,)
        ).fetchone()
        return json.loads(r["data"]) if r else None


def list_papers():
    with connect() as c:
        rows = c.execute(
            "SELECT id,data FROM papers ORDER BY created_at DESC LIMIT 100"
        ).fetchall()

        out = []
        for r in rows:
            d = json.loads(r["data"])
            d["id"] = r["id"]
            d.pop("sets", None)
            out.append(d)

        return out


def counts():
    with connect() as c:
        return {
            "documents": c.execute(
                "SELECT COUNT(*) n FROM documents"
            ).fetchone()["n"],
            "papers": c.execute(
                "SELECT COUNT(*) n FROM papers"
            ).fetchone()["n"]
        }
