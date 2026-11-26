import sqlite3
import json

from contextlib import contextmanager
from datetime import datetime

from config import DB_PATH, initialize_directories


@contextmanager
def get_connection():
    initialize_directories()

    connection = sqlite3.connect(
        DB_PATH, timeout=10
    )
    connection.row_factory = sqlite3.Row

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


# Initialize database
def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                declared_extension TEXT,
                actual_type TEXT,
                status TEXT,
                risk_score INTEGER,
                severity TEXT,
                findings TEXT,
                scan_source TEXT DEFAULT 'Manual',
                scanned_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_severity
            ON scan_history(severity)
        """)


# Save scan result
def save_scan(result, source="Manual"):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO scan_history (
                filename,
                file_path,
                declared_extension,
                actual_type,
                status,
                risk_score,
                severity,
                findings,
                scan_source,
                scanned_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result["filename"],
            result["path"],
            result["declared_extension"],
            result["actual_type"],
            result["status"],
            result["risk_score"],
            result["severity"],
            json.dumps(result["risk_reasons"]),
            source,
            datetime.now().astimezone().isoformat(
                timespec="seconds"
            )
        ))

        return cursor.lastrowid


# Convert database records into dictionaries
def format_records(records):
    results = []

    for record in records:
        item = dict(record)
        item["findings"] = json.loads(
            item["findings"] or "[]"
        )
        results.append(item)

    return results


# Retrieve scan history
def get_scan_history(limit=100):
    with get_connection() as connection:
        records = connection.execute("""
            SELECT * FROM scan_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return format_records(records)


# Retrieve security incidents
def get_threat_history(limit=100):
    with get_connection() as connection:
        records = connection.execute("""
            SELECT * FROM scan_history
            WHERE risk_score > 0
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()

        return format_records(records)


# Retrieve dashboard statistics
def get_statistics():
    statistics = {
        "total_scans": 0,
        "no_risk": 0,
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
        "unknown": 0,
        "suspicious": 0
    }

    with get_connection() as connection:
        records = connection.execute("""
            SELECT severity, COUNT(*) AS count
            FROM scan_history
            GROUP BY severity
        """).fetchall()

        for record in records:
            severity = record["severity"]
            count = record["count"]

            statistics["total_scans"] += count

            if severity == "None":
                statistics["no_risk"] += count

            elif severity and severity.lower() in (
                "low", "medium", "high", "critical"
            ):
                statistics[severity.lower()] += count

            else:
                statistics["unknown"] += count

        statistics["suspicious"] = sum(
            statistics[level]
            for level in (
                "low", "medium", "high", "critical"
            )
        )

    return statistics

def search_threat_history(
    search="",
    severity="All Severities",
    source="All Sources",
    limit=None
):
    query = """
        SELECT * FROM scan_history
        WHERE risk_score > 0
    """

    parameters = []

    if search.strip():
        keyword = f"%{search.strip()}%"

        query += """
            AND (
                filename LIKE ?
                OR file_path LIKE ?
                OR findings LIKE ?
            )
        """

        parameters.extend([
            keyword, keyword, keyword
        ])

    if severity != "All Severities":
        query += " AND severity = ?"
        parameters.append(severity)

    if source != "All Sources":
        query += " AND scan_source = ?"
        parameters.append(source)

    query += " ORDER BY id DESC"

    if limit is not None:
        query += " LIMIT ?"
        parameters.append(limit)

    with get_connection() as connection:
        records = connection.execute(
            query, parameters
        ).fetchall()

        return format_records(records)
