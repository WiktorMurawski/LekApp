# wsgi_test.py
from wsgiref.simple_server import make_server
from app import app  # Import your Flask app

# Flask's app is already WSGI-compliant
with make_server("", 8000, app) as server:
    print("Serving on http://localhost:8000 ...")
    server.serve_forever()
