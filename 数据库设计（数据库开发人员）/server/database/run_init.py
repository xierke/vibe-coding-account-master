#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日常记账APP - 数据库初始化脚本执行器
读取 init.sql 并通过 mysql-connector-python 执行
"""

import mysql.connector
import os
import sys
import io

# 强制 stdout 使用 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "wyx4022",
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
}

SQL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "init.sql")


def read_sql_statements(filepath):
    """Read SQL file, split by semicolons into individual statements."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    statements = []
    current = []

    for line in content.split("\n"):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("--"):
            continue
        if stripped.startswith("/*") and stripped.endswith("*/"):
            continue

        current.append(line)

        if stripped.endswith(";"):
            stmt = "\n".join(current).rstrip(";").strip()
            if stmt:
                statements.append(stmt)
            current = []

    # 残留
    leftover = "\n".join(current).strip()
    if leftover:
        statements.append(leftover)

    return statements


def main():
    if not os.path.exists(SQL_FILE):
        print(f"ERROR: SQL file not found: {SQL_FILE}")
        sys.exit(1)

    statements = read_sql_statements(SQL_FILE)
    print(f"Found {len(statements)} SQL statements in init.sql\n")

    print("Connecting to MySQL...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    ok = 0
    err = 0

    for idx, stmt in enumerate(statements, start=1):
        first_line = stmt.split("\n")[0][:80]
        try:
            cursor.execute(stmt)
            ok += 1
            print(f"  [{idx:02d}] OK {first_line}")
        except mysql.connector.Error as e:
            err += 1
            print(f"  [{idx:02d}] ERROR: {e}")
            print(f"       SQL: {first_line}")

    conn.commit()

    print(f"\n--- {ok} OK, {err} ERR ---\n")
    print("=== Verification ===\n")

    cursor.execute("SHOW DATABASES LIKE 'account'")
    dbs = cursor.fetchall()
    print(f"  Database 'account': {'OK - Created' if dbs else 'FAILED'}")

    cursor.execute("USE account")
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"  Tables ({len(tables)}): {[t[0] for t in tables]}")

    cursor.execute("SELECT COUNT(*) FROM categories")
    cat_count = cursor.fetchone()[0]
    print(f"  Default categories: {cat_count} rows")

    cursor.execute("SELECT name, icon, type, color FROM categories ORDER BY type, sort_order")
    for name, icon, cat_type, color in cursor.fetchall():
        type_label = "expense" if cat_type == "expense" else "income "
        print(f"    {icon} {name:6s} ({type_label}) {color}")

    cursor.close()
    conn.close()
    print("\n=== Database init complete ===")


if __name__ == "__main__":
    main()
