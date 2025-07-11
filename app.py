from flask import Flask, render_template, request, jsonify
import sqlite3
from etl.csv_importer import update_database_from_csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_entries():
    query = request.args.get('query', '').lower()

    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    sql_query = f"""
        SELECT * FROM {TABLE_NAME}
        WHERE [Nazwa Produktu Leczniczego] LIKE ?
        LIMIT 1000
    """
    c.execute(sql_query, (f'%{query}%',))
    column_names = [desc[0] for desc in c.description]
    rows = [dict(row) for row in c.fetchall()]
    conn.close()

    return jsonify({
        'length': len(rows),
        'columns': column_names,
        'rows': [dict(row) for row in rows]
    })

if __name__ == '__main__':
    CSV_URL = "https://rejestry.ezdrowie.gov.pl/api/rpl/medicinal-products/public-pl-report/get-csv"
    CSV_FILE = "downloads/rejestr.csv"
    SQLITE_DB = "database/lekidatabase.db"
    TABLE_NAME = "leki"

    try:
        update_database_from_csv(CSV_URL, CSV_FILE, SQLITE_DB, TABLE_NAME)
    except Exception as e:
        print(f"Something went wrong: {e}")

    debug = True
    app.run(debug=debug)
