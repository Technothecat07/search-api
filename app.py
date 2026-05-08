from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)

# Enable CORS
CORS(app)

# Database path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "students.db")

# Master unlock password
MASTER_PASSWORD = "Technothecat07"

@app.route("/")
def home():

    return jsonify({
        "status": "online"
    })

@app.route("/count")
def count():

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM students")

    total = cur.fetchone()[0]

    conn.close()

    return jsonify({
        "records": total
    })

@app.route("/search")
def search():

    query = request.args.get("q", "").strip()
    unlock_password = request.args.get("password", "").strip()

    if not query:
        return jsonify([])

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    cur = conn.cursor()

    sql = """
    SELECT * FROM students
    WHERE
        name LIKE ? OR
        user_id LIKE ? OR
        email LIKE ? OR
        mobile LIKE ?
    LIMIT 50
    """

    q = f"%{query}%"

    cur.execute(sql, (q, q, q, q))

    rows = []

    for r in cur.fetchall():

        row = dict(r)

        # Hide mobile and password unless correct password entered
        if unlock_password != MASTER_PASSWORD:

            row["mobile"] = "HIDDEN"
            row["password"] = "PROTECTED"

        rows.append(row)

    conn.close()

    return jsonify(rows)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
