from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import logging
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

# Enable CORS for Blogspot
CORS(app)

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["30 per minute"]
)

# Create logs folder
os.makedirs("logs", exist_ok=True)

# Logging setup
logging.basicConfig(
    filename="logs/requests.log",
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)

# Home route
@app.route("/")
def home():
    return jsonify({
        "status": "online"
    })

# Search route
@app.route("/search")
@limiter.limit("15 per minute")
def search():

    # API key validation
    #key = request.headers.get("x-api-key")

    #if key != API_KEY:
     #   return jsonify({
     #       "error": "Invalid API key"
     #   }), 403

    # Get query
    query = request.args.get("q", "").strip()

    # Prevent tiny spam queries
    if len(query) < 2:
        return jsonify([])

    # Log searches
    logging.info(
        f"SEARCH: {query} | IP: {request.remote_addr}"
    )

    # Connect database
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    # SQL search
    sql = """
    SELECT * FROM students
    WHERE
        user_id LIKE ? OR
        password LIKE ? OR
        name LIKE ? OR
        father LIKE ? OR
        mobile LIKE ? OR
        course LIKE ? OR
        section LIKE ? OR
        roll_no LIKE ? OR
        email LIKE ? OR
        city LIKE ?
    LIMIT 50
    """

    q = f"%{query}%"

    cur.execute(sql, (
        q, q, q, q, q,
        q, q, q, q, q
    ))

    rows = [dict(r) for r in cur.fetchall()]

    conn.close()

    return jsonify(rows)

# Start server
if __name__ == "__main__":
    app.run(debug=True)