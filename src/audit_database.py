from __future__ import annotations
import json, sqlite3
from datetime import datetime, timezone
from .config import DB_PATH

class AuditDatabase:
    def __init__(self, path=DB_PATH):
        self.path = str(path); self._init()
    def connect(self): return sqlite3.connect(self.path)
    def _init(self):
        with self.connect() as c: c.execute("CREATE TABLE IF NOT EXISTS analyses (id INTEGER PRIMARY KEY, timestamp TEXT, case_id TEXT, score REAL, reason TEXT, recommendation TEXT, review_status TEXT, reviewer_comments TEXT DEFAULT '', payload TEXT)")
    def save(self, record):
        with self.connect() as c:
            cur=c.execute("INSERT INTO analyses(timestamp,case_id,score,reason,recommendation,review_status,payload) VALUES(?,?,?,?,?,?,?)", (datetime.now(timezone.utc).isoformat(),record["case"]["case_id"],record["score"]["score"],record["classification"]["reason"],record["recommendation"]["recommendation"],"Pending" if record["recommendation"]["human_review_required"] else "Not required",json.dumps(record,default=str)))
            return cur.lastrowid
    def list(self, case_id=""):
        with self.connect() as c:
            c.row_factory=sqlite3.Row
            rows=c.execute("SELECT * FROM analyses WHERE case_id LIKE ? ORDER BY id DESC",(f"%{case_id}%",)).fetchall()
        return [dict(r) for r in rows]
    def review(self, row_id, status, comments):
        with self.connect() as c: c.execute("UPDATE analyses SET review_status=?, reviewer_comments=? WHERE id=?",(status,comments,row_id))

