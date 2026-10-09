from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS requests (
 request_id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL,
 department TEXT NOT NULL, channel TEXT NOT NULL, declared_urgency TEXT NOT NULL,
 submitted_at_utc TEXT NOT NULL, status TEXT NOT NULL, is_synthetic INTEGER NOT NULL CHECK(is_synthetic IN (0,1))
);
CREATE TABLE IF NOT EXISTS processing_runs (
 processing_run_id TEXT PRIMARY KEY, request_id TEXT NOT NULL REFERENCES requests(request_id),
 processing_mode TEXT NOT NULL, processed_at_utc TEXT NOT NULL, engine_version TEXT NOT NULL,
 proposed_category TEXT, proposed_priority TEXT, confidence REAL NOT NULL,
 evidence_json TEXT NOT NULL, raw_output_json TEXT, validation_status TEXT NOT NULL, error_message TEXT
);
CREATE TABLE IF NOT EXISTS reviews (
 review_id TEXT PRIMARY KEY, request_id TEXT NOT NULL REFERENCES requests(request_id),
 processing_run_id TEXT NOT NULL REFERENCES processing_runs(processing_run_id), reviewer_name TEXT NOT NULL,
 reviewed_at_utc TEXT NOT NULL, final_category TEXT NOT NULL, final_priority TEXT NOT NULL,
 category_corrected INTEGER NOT NULL CHECK(category_corrected IN (0,1)),
 priority_corrected INTEGER NOT NULL CHECK(priority_corrected IN (0,1)), rationale TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
CREATE INDEX IF NOT EXISTS idx_runs_request ON processing_runs(request_id);
CREATE INDEX IF NOT EXISTS idx_reviews_request ON reviews(request_id);
"""


class Repository:
    def __init__(self, path: str | Path):
        self.path = str(path)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as conn:
            conn.executescript(SCHEMA)

    def insert_request(self, record: dict) -> None:
        with self.connection() as conn:
            conn.execute("""INSERT INTO requests VALUES (:request_id,:title,:description,:department,:channel,:declared_urgency,:submitted_at_utc,:status,:is_synthetic)""", record)

    def insert_run(self, record: dict) -> None:
        record = {**record, "evidence_json": json.dumps(record["evidence"], sort_keys=True)}
        with self.connection() as conn:
            conn.execute("""INSERT INTO processing_runs (processing_run_id,request_id,processing_mode,processed_at_utc,engine_version,proposed_category,proposed_priority,confidence,evidence_json,raw_output_json,validation_status,error_message)
            VALUES (:processing_run_id,:request_id,:processing_mode,:processed_at_utc,:engine_version,:proposed_category,:proposed_priority,:confidence,:evidence_json,:raw_output_json,:validation_status,:error_message)""", record)

    def update_status(self, request_id: str, status: str) -> None:
        with self.connection() as conn:
            if conn.execute("UPDATE requests SET status=? WHERE request_id=?", (status, request_id)).rowcount != 1:
                raise KeyError(f"Unknown request: {request_id}")

    def insert_review(self, record: dict) -> None:
        with self.connection() as conn:
            conn.execute("""INSERT INTO reviews VALUES (:review_id,:request_id,:processing_run_id,:reviewer_name,:reviewed_at_utc,:final_category,:final_priority,:category_corrected,:priority_corrected,:rationale)""", record)

    def requests_for_review(self) -> list[dict]:
        with self.connection() as conn:
            rows = conn.execute("""SELECT r.*, p.processing_run_id,p.proposed_category,p.proposed_priority,p.confidence,p.evidence_json,p.processing_mode,p.processed_at_utc
            FROM requests r JOIN processing_runs p ON p.request_id=r.request_id
            WHERE r.status='needs_review' AND p.validation_status='valid'
            AND p.processed_at_utc=(SELECT MAX(p2.processed_at_utc) FROM processing_runs p2 WHERE p2.request_id=r.request_id)
            ORDER BY p.processed_at_utc""").fetchall()
        return [dict(row) for row in rows]

    def report_rows(self) -> list[dict]:
        with self.connection() as conn:
            rows = conn.execute("""SELECT r.request_id,r.department,r.status,r.submitted_at_utc,r.is_synthetic,p.processing_mode,p.proposed_category,p.proposed_priority,
              CASE WHEN EXISTS(SELECT 1 FROM reviews v WHERE v.request_id=r.request_id) THEN 1 ELSE 0 END reviewed,
              CASE WHEN EXISTS(SELECT 1 FROM reviews v WHERE v.request_id=r.request_id AND (v.category_corrected=1 OR v.priority_corrected=1)) THEN 1 ELSE 0 END corrected
              FROM requests r LEFT JOIN processing_runs p ON p.processing_run_id=(
                SELECT p2.processing_run_id FROM processing_runs p2
                WHERE p2.request_id=r.request_id AND p2.validation_status='valid'
                ORDER BY p2.processed_at_utc DESC, p2.processing_run_id DESC LIMIT 1
              )""").fetchall()
        return [dict(row) for row in rows]

    def has_request(self, request_id: str) -> bool:
        with self.connection() as conn:
            return conn.execute("SELECT 1 FROM requests WHERE request_id=?", (request_id,)).fetchone() is not None
