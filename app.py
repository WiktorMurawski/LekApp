from flask import Flask, render_template, request, jsonify
import sqlite3
from etl.csv_importer import update_database_from_csv

app = Flask(__name__)

CSV_URL = "https://rejestry.ezdrowie.gov.pl/api/rpl/medicinal-products/public-pl-report/get-csv"
CSV_FILE = "downloads/rejestr.csv"
SQLITE_DB = "database/lekidatabase.db"
TABLE_NAME = "leki"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search_entries():
    query = request.args.get('query', '').lower()
    search_type = request.args.get('type', 'nazwa')

    conn = sqlite3.connect(SQLITE_DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    columns = [
        '"Identyfikator Produktu Leczniczego" AS "Identyfikator Produktu Leczniczego"',
        '"Nazwa Produktu Leczniczego" AS "Nazwa Produktu Leczniczego"',
        '"Nazwa powszechnie stosowana" AS "Nazwa powszechnie stosowana"',
        '"Nazwa poprzednia produktu" AS "Nazwa poprzednia produktu"',
        '"Substancja czynna" AS "Substancja czynna"',
        # '"Rodzaj preparatu" AS "Rodzaj preparatu"',
        # '"Zakaz stosowania u zwierząt" AS "Zakaz stosowania u zwierząt"',
        '"Droga podania _ Gatunek _ Tkanka _ Okres karencji" AS "Droga podania"',
        '"Moc" AS "Moc"',
        '"Postać farmaceutyczna" AS "Postać farmaceutyczna"',
        '"Typ procedury" AS "Typ procedury"',
        # '"Numer pozwolenia" AS "Numer pozwolenia"',
        '"Ważność pozwolenia" AS "Ważność pozwolenia"',
        '"Kod ATC" AS "Kod ATC"',
        '"Podmiot odpowiedzialny" AS "Podmiot odpowiedzialny"',
        '"Opakowanie" AS "Opakowanie"',
        # '"Nazwa wytwórcy" AS "Nazwa wytwórcy"',
        # '"Nazwa importera" AS "Nazwa importera"',
        # '"Nazwa wytwórcy_importera" AS "Nazwa wytwórcy-importera"',
        # '"Kraj wytwórcy" AS "Kraj wytwórcy"',
        # '"Kraj importera" AS "Kraj importera"',
        # '"Kraj wytwórcy_importera" AS "Kraj wytwórcy-importera"',
        # '"Podmiot odpowiedzialny w kraju eksportu" AS "Podmiot odpowiedzialny w kraju eksportu"',
        # '"Kraj eksportu" AS "Kraj eksportu"',
        # '"Podstawa prawna wniosku" AS "Podstawa prawna wniosku"',
        # '"Ulotka" AS "Ulotka"',
        # '"Charakterystyka" AS "Charakterystyka"',
        # '"Etykieto_ulotka" AS "Etykieto-ulotka"',
        # '"Ulotka importu równoległego" AS "Ulotka importu równoległego"',
        # '"Etykieto_ulotka importu równoległego" AS "Etykieto-ulotka importu równoległego"',
        # '"Oznakowanie opakowań importu równoległego" AS "Oznakowanie opakowań importu równoległego"',
        # '"Materiały edukacyjne dla osoby wykonującej zawód medyczny" AS "Materiały edukacyjne dla osoby wykonującej zawód medyczny"',
        # '"Materiały edukacyjne dla pacjenta" AS "Materiały edukacyjne dla pacjenta"',
    ]

    where_clause = """
        "Rodzaj Preparatu" = 'Ludzki' AND (
            "Nazwa Produktu Leczniczego" LIKE ?
            OR "Nazwa powszechnie stosowana" LIKE ?
            OR "Nazwa poprzednia produktu" LIKE ?
        )
    """
    params = [f'%{query}%'] * 3

    if search_type == "substancja":
        where_clause = """
            "Rodzaj Preparatu" = 'Ludzki' AND "Substancja czynna" LIKE ?
        """
        params = [f'%{query}%']
        print("substancja!")

    sql_query = f"""
        SELECT 
            {",\n    ".join(columns)}
        FROM {TABLE_NAME}
        WHERE {where_clause}
        LIMIT 1000
    """

    c.execute(sql_query, params)
    column_names = [desc[0] for desc in c.description]
    rows = [dict(row) for row in c.fetchall()]
    conn.close()

    return jsonify({
        'length': len(rows),
        'columns': column_names,
        'rows': [dict(row) for row in rows]
    })

if __name__ == '__main__':

    try:
        update_database_from_csv(CSV_URL, CSV_FILE, SQLITE_DB, TABLE_NAME)
    except Exception as e:
        print(f"Something went wrong: {e}")

    debug = True
    app.run(debug=debug)
