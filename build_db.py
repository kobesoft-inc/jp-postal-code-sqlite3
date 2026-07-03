#!/usr/bin/env python3
"""日本郵便のKEN_ALL(郵便番号)データをダウンロードし、SQLite3データベースを生成する。"""

import argparse
import csv
import io
import sqlite3
import sys
import urllib.request
import zipfile

KEN_ALL_URL = "https://www.post.japanpost.jp/service/search/zipcode/download/utf/zip/utf_ken_all.zip"

SCHEMA = """
CREATE TABLE IF NOT EXISTS postal_codes (
    jis_code        TEXT NOT NULL,
    old_zip_code    TEXT NOT NULL,
    zip_code        TEXT NOT NULL,
    pref_kana       TEXT NOT NULL,
    city_kana       TEXT NOT NULL,
    town_kana       TEXT NOT NULL,
    pref            TEXT NOT NULL,
    city            TEXT NOT NULL,
    town            TEXT NOT NULL,
    is_multi_zip    INTEGER NOT NULL,
    has_koaza_banchi INTEGER NOT NULL,
    has_chome       INTEGER NOT NULL,
    is_multi_town   INTEGER NOT NULL,
    update_flag     INTEGER NOT NULL,
    change_reason   INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_postal_codes_zip_code ON postal_codes (zip_code);
"""

COLUMNS = [
    "jis_code", "old_zip_code", "zip_code",
    "pref_kana", "city_kana", "town_kana",
    "pref", "city", "town",
    "is_multi_zip", "has_koaza_banchi", "has_chome", "is_multi_town",
    "update_flag", "change_reason",
]


def fetch_csv_rows(url):
    with urllib.request.urlopen(url) as res:
        data = res.read()
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        csv_name = next(name for name in zf.namelist() if name.lower().endswith(".csv"))
        with zf.open(csv_name) as f:
            text = io.TextIOWrapper(f, encoding="utf-8")
            yield from csv.reader(text)


def build_database(db_path, url):
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA)
        conn.execute("DELETE FROM postal_codes")
        placeholders = ",".join("?" for _ in COLUMNS)
        conn.executemany(
            f"INSERT INTO postal_codes ({','.join(COLUMNS)}) VALUES ({placeholders})",
            fetch_csv_rows(url),
        )
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM postal_codes").fetchone()[0]
        print(f"{count} 件の郵便番号データを {db_path} に書き込みました。", file=sys.stderr)
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-o", "--output", default="jp_postal_code.db", help="出力先のSQLite3ファイルパス")
    parser.add_argument("--url", default=KEN_ALL_URL, help="KEN_ALL CSV(zip)のダウンロードURL")
    args = parser.parse_args()
    build_database(args.output, args.url)


if __name__ == "__main__":
    main()
