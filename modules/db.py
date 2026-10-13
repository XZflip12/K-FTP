import sqlite3
from pathlib import Path

from modules.config import (
    DB_FILE_NAME,
    DEFAULT_DB_HOST,
    DEFAULT_DB_PASS,
    DEFAULT_DB_PORT,
    DEFAULT_DB_USER,
    KEY_HOST,
    KEY_ID,
    KEY_PASSWORD,
    KEY_PORT,
    KEY_USERNAME,
    SQL_COUNT_PROFILES,
    SQL_CREATE_TABLE,
    SQL_DELETE_PROFILE,
    SQL_INSERT_DEFAULT,
    SQL_INSERT_PROFILE,
    SQL_SELECT_ALL,
    SQL_SELECT_BY_ID,
)

DB_PATH = Path(__file__).parent / DB_FILE_NAME


def create_profiles_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(SQL_CREATE_TABLE)

    cursor.execute(SQL_COUNT_PROFILES)
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute(SQL_INSERT_DEFAULT)

    conn.commit()
    conn.close()


def save_profile(host, username, password, port=DEFAULT_DB_PORT):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(SQL_INSERT_PROFILE, (host, username, password, port))
    conn.commit()

    new_id = cursor.lastrowid
    conn.close()
    return new_id


def delete_profile(profile_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(SQL_DELETE_PROFILE, (profile_id,))
    conn.commit()
    conn.close()


def get_profiles():
    create_profiles_table()

    profiles = []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(SQL_SELECT_ALL)
    rows = cursor.fetchall()
    for row in rows:
        profiles.append(
            {
                KEY_ID: row[0],
                KEY_HOST: row[1],
                KEY_USERNAME: row[2],
                KEY_PASSWORD: row[3],
                KEY_PORT: row[4],
            }
        )
    conn.close()
    return profiles


def get_profile(profile_id):
    create_profiles_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(SQL_SELECT_BY_ID, (profile_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return row

    return (DEFAULT_DB_HOST, DEFAULT_DB_USER, DEFAULT_DB_PASS, DEFAULT_DB_PORT)
