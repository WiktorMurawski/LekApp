from flask import Flask, render_template, request, jsonify
import sqlite3
from etl.csv_importer import update_database_from_csv

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    content = data.get('content')
    if content:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO entries (content) VALUES (?)', (content,))
        conn.commit()
        conn.close()
        return jsonify({"message": "Saved"}), 200
    return jsonify({"message": "Invalid input"}), 400

@app.route('/entries', methods=['GET'])
def get_entries():
    conn = sqlite3.connect('lekidatabase.db')
    c = conn.cursor()
    c.execute('SELECT * FROM entries')
    rows = c.fetchall()
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    CSV_URL = "https://rejestry.ezdrowie.gov.pl/api/rpl/medicinal-products/public-pl-report/get-csv"  # Put your CSV URL here
    CSV_FILE = "rejestr.csv"
    SQLITE_DB = "lekidatabase.db"
    TABLE_NAME = "leki"

    try:
        update_database_from_csv(CSV_URL, CSV_FILE, SQLITE_DB, TABLE_NAME)
    except Exception as e:
        print(f"Something went wrong: {e}")

    # init_db()
    debug = True
    app.run(debug=debug)
