import requests
import os
import re
import csv
import sqlite3
import shutil

def download_csv(url : str, filename: str) -> None:
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as f:
        f.write(response.content)
    print(f"CSV downloaded to '{filename}'.")

def sanitize_column_name(name: str) -> str:
    """
    Converts column names into safe SQLite identifiers.
    Keeps alphanumerics and underscores. Replaces others with underscores.
    """
    name = name.strip()
    # Replace invalid characters with underscore
    name = re.sub(r'[^\w ]', '_', name)
    # Ensure it doesn't start with a number
    if re.match(r'^\d', name):
        name = f'col_{name}'
    return name

def create_table_and_insert(csv_file: str, db_file: str, table_name: str) -> None:
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file '{csv_file}' not found.")
    
    with open(csv_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)

        # Create sanitized column names for SQLite
        clean_columns = [sanitize_column_name(h) for h in headers]
        columns_def = ', '.join([f'"{col}" TEXT' for col in clean_columns])
        quoted_columns = ', '.join(f'"{c}"' for c in clean_columns)
        placeholders = ', '.join(['?'] * len(clean_columns))
        insert_query = f'INSERT INTO "{table_name}" ({quoted_columns}) VALUES ({placeholders})'

        # print(f"INSERT QUERY = {insert_query}")

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        try:
            cursor.execute("PRAGMA synchronous = OFF;")
            cursor.execute("PRAGMA journal_mode = MEMORY;")

            cursor.execute("BEGIN TRANSACTION;")
            cursor.execute(f'DROP TABLE IF EXISTS "{table_name}";')
            cursor.execute(f'CREATE TABLE "{table_name}" ({columns_def});')

            print("Created table.")

            cursor.executemany(insert_query, reader)

            conn.commit()
            print(f"Data inserted into '{table_name}' in DB '{db_file}'.")
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Failed to create table and insert data: {e}")
        finally:
            conn.close()

def atomic_replace(src: str, dest: str) -> None:
    """
    Atomically replaces dest with src.
    This is safe and prevents any period where the DB file is missing.
    A backup of the old DB is kept as dest + '.backup'.
    """
    if os.path.exists(dest):
        shutil.copy2(dest, dest + '.backup')  # optional, for rollback
    os.replace(src, dest)
    print(f"Replaced '{dest}' with '{src}' (atomic swap).")

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY, content TEXT)''')
    conn.commit()
    conn.close()

def update_database_from_csv(url: str, csv_filename: str, db_filename: str, table_name: str) -> None:
    temp_db = db_filename + ".temp"

    print("Starting CSV download...")
    download_csv(url, csv_filename)

    print("Creating and populating temporary database...")
    create_table_and_insert(csv_filename, temp_db, table_name)

    print("Replacing old database with new one...")
    atomic_replace(temp_db, db_filename)

    print("Update complete.")