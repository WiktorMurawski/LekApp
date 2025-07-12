# update_db.py
from app import CSV_URL, CSV_FILE, SQLITE_DB, TABLE_NAME
from etl.csv_importer import update_database_from_csv

def main():
    try:
        update_database_from_csv(CSV_URL, CSV_FILE, SQLITE_DB, TABLE_NAME)
        print("Database update successful.")
    except Exception as e:
        print(f"Database update failed: {e}")

if __name__ == '__main__':
    main()