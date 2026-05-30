#!/usr/bin/env python3
"""数据模型 - SQLite 数据库定义"""
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ai_uart.db")


def get_db_path() -> str:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(get_db_path(), timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化数据库表结构"""
    conn = get_connection()
    conn.executescript("""
        -- 测试会话
        CREATE TABLE IF NOT EXISTS test_sessions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            name            TEXT,
            module          TEXT,
            script_file     TEXT,
            port            TEXT,
            baudrate        INTEGER,
            model           TEXT,
            case_level      TEXT,
            status          TEXT DEFAULT 'running',
            total_cases     INTEGER DEFAULT 0,
            passed          INTEGER DEFAULT 0,
            failed          INTEGER DEFAULT 0,
            started_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at        TIMESTAMP,
            summary         TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 测试用例执行记录
        CREATE TABLE IF NOT EXISTS test_case_runs (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id        INTEGER REFERENCES test_sessions(id),
            sheet_name        TEXT,
            excel_row_id      INTEGER,
            test_group        TEXT,
            case_name         TEXT,
            case_level        TEXT DEFAULT 'P0',
            applicable_models TEXT,
            at_command        TEXT,
            send_data         TEXT,
            expected_result   TEXT,
            actual_result     TEXT,
            duration_ms       INTEGER,
            status            TEXT DEFAULT 'PENDING',
            fail_reason       TEXT,
            ai_analysis       TEXT,
            executed_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 串口原始日志
        CREATE TABLE IF NOT EXISTS serial_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER,
            direction   TEXT,
            data_hex    TEXT,
            data_ascii  TEXT,
            timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- 本地缺陷
        CREATE TABLE IF NOT EXISTS local_defects (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            test_session_id   INTEGER,
            test_case_run_id  INTEGER,
            title             TEXT,
            description       TEXT,
            severity          INTEGER DEFAULT 2,
            priority          INTEGER DEFAULT 1,
            status            TEXT DEFAULT 'local',
            lingji_id         TEXT,
            lingji_url        TEXT,
            local_file        TEXT,
            confirmed_by      TEXT,
            created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at      TIMESTAMP,
            synced_at         TIMESTAMP
        );

        -- 知识图谱三元组
        CREATE TABLE IF NOT EXISTS knowledge_triples (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            subject     TEXT,
            predicate   TEXT,
            object      TEXT,
            context     TEXT,
            confidence  REAL DEFAULT 1.0,
            source      TEXT DEFAULT 'test_run',
            session_id  INTEGER,
            created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_triples_subject   ON knowledge_triples(subject);
        CREATE INDEX IF NOT EXISTS idx_triples_predicate  ON knowledge_triples(predicate);
        CREATE INDEX IF NOT EXISTS idx_triples_object     ON knowledge_triples(object);
        CREATE INDEX IF NOT EXISTS idx_case_runs_session  ON test_case_runs(session_id);
        CREATE INDEX IF NOT EXISTS idx_case_runs_status   ON test_case_runs(status);
    """)
    conn.commit()
    conn.close()


# --- 便捷查询函数 ---

def create_session(name: str, module: str, port: str = "", baudrate: int = 115200,
                   model: str = "", case_level: str = "P0", script_file: str = "") -> int:
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO test_sessions (name, module, script_file, port, baudrate, model, case_level, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'running')
    """, (name, module, script_file, port, baudrate, model, case_level))
    session_id = cur.lastrowid
    conn.commit()
    conn.close()
    return session_id


def end_session(session_id: int, summary: str = ""):
    conn = get_connection()
    conn.execute("""
        UPDATE test_sessions SET status='completed', ended_at=CURRENT_TIMESTAMP, summary=?
        WHERE id=?
    """, (summary, session_id))
    conn.commit()
    conn.close()


def update_session_stats(session_id: int):
    conn = get_connection()
    row = conn.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN status='PASS' THEN 1 ELSE 0 END) as passed,
               SUM(CASE WHEN status='FAIL' THEN 1 ELSE 0 END) as failed
        FROM test_case_runs WHERE session_id=?
    """, (session_id,)).fetchone()
    conn.execute("""
        UPDATE test_sessions SET total_cases=?, passed=?, failed=? WHERE id=?
    """, (row['total'], row['passed'], row['failed'], session_id))
    conn.commit()
    conn.close()


def add_case_run(session_id: int, **kwargs) -> int:
    conn = get_connection()
    cur = conn.execute("""
        INSERT INTO test_case_runs (session_id, sheet_name, excel_row_id, test_group,
            case_name, case_level, applicable_models, at_command, send_data,
            expected_result, actual_result, duration_ms, status, fail_reason, ai_analysis)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        kwargs.get('sheet_name'),
        kwargs.get('excel_row_id'),
        kwargs.get('test_group'),
        kwargs.get('case_name'),
        kwargs.get('case_level', 'P0'),
        kwargs.get('applicable_models'),
        kwargs.get('at_command'),
        kwargs.get('send_data'),
        kwargs.get('expected_result'),
        kwargs.get('actual_result'),
        kwargs.get('duration_ms'),
        kwargs.get('status', 'PENDING'),
        kwargs.get('fail_reason'),
        kwargs.get('ai_analysis'),
    ))
    case_run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return case_run_id


if __name__ == "__main__":
    init_db()
    print(f"数据库已初始化: {get_db_path()}")
