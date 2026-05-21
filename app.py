from flask import Flask, render_template, request, redirect
import hashlib
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

ORIGINAL_FOLDER = "originals"
UPLOAD_FOLDER = "uploads"

os.makedirs(ORIGINAL_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# DATABASE SETUP
def init_db():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()
    cursor.execute("""

        CREATE TABLE IF NOT EXISTS files (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT UNIQUE,

            filetype TEXT,

            filesize TEXT,

            hash TEXT,

            upload_time TEXT,

            status TEXT
        )

    """)


    cursor.execute("""

        CREATE TABLE IF NOT EXISTS verification_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT,

            verification_time TEXT,

            result TEXT,

            uploaded_hash TEXT
        )

    """)

    conn.commit()
    conn.close()
   


init_db()


def generate_hash(filepath):

    sha256 = hashlib.sha256()

    with open(filepath, "rb") as file:

        while chunk := file.read(4096):
            sha256.update(chunk)

    return sha256.hexdigest()
def format_size(size):

    if size < 1024:
        return f"{size} B"

    elif size < 1024 * 1024:
        return f"{size / 1024:.2f} KB"

    else:
        return f"{size / (1024 * 1024):.2f} MB"


@app.route('/')
def home():

    return render_template("index.html")

# REGISTER ORIGINAL FILE
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        file = request.files['file']

        if file.filename == '':
            return redirect('/register')

        filepath = os.path.join(
            ORIGINAL_FOLDER,
            file.filename
        )

        # Prevent duplicate trusted files
        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM files
            WHERE filename = ?
        """, (file.filename,))

        existing_file = cursor.fetchone()

        if existing_file:

            conn.close()

            return render_template(
                "register.html",
                duplicate=True,
                filename=file.filename
            )

        file.save(filepath)

        file_hash = generate_hash(filepath)

        filesize = format_size(
            os.path.getsize(filepath)
        )

        filetype = file.filename.split('.')[-1].upper()

        upload_time = datetime.now().strftime(
            "%d %B %Y %I:%M %p"
        )

        cursor.execute("""

            INSERT INTO files
            (filename, filetype, filesize,
             hash, upload_time, status)

            VALUES (?, ?, ?, ?, ?, ?)

        """, (

            file.filename,
            filetype,
            filesize,
            file_hash,
            upload_time,
            "Trusted"

        ))

        conn.commit()
        conn.close()

        return render_template(
            "register.html",
            success=True,
            filename=file.filename,
            file_hash=file_hash,
            filesize=filesize,
            filetype=filetype
        )

    return render_template("register.html")


# VERIFY FILE
@app.route('/verify', methods=['GET', 'POST'])
def verify():

    if request.method == 'POST':

        file = request.files['file']

        if file.filename == '':
            return redirect('/verify')

        filepath = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        file.save(filepath)

        uploaded_hash = generate_hash(filepath)

        verification_time = datetime.now().strftime(
            "%d %B %Y %I:%M %p"
        )

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()

        # Check original file
        cursor.execute("""
            SELECT hash
            FROM files
            WHERE filename = ?
        """, (file.filename,))
        result = cursor.fetchone()
        if result:
            original_hash = result[0]

            if uploaded_hash == original_hash:

                status = "VERIFIED ✅"
                risk = "SAFE"
            else:

                status = "TAMPERED ❌"
                risk = "HIGH RISK"
        else:

            status = "NO ORIGINAL FILE FOUND"
            risk = "UNKNOWN"

        cursor.execute("""

            INSERT INTO verification_history
            (filename, verification_time,
             result, uploaded_hash)

            VALUES (?, ?, ?, ?)

        """, (

            file.filename,
            verification_time,
            status,
            uploaded_hash

        ))
        conn.commit()
        conn.close()
        return render_template(

            "verify.html",

            status=status,
            filename=file.filename,
            uploaded_hash=uploaded_hash,
            risk=risk,
            verification_time=verification_time

        )

    return render_template("verify.html")


@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT *
        FROM files
        ORDER BY id DESC
    """)
    files = cursor.fetchall()
    conn.close()
    return render_template(
        "dashboard.html",
        files=files
    )

if __name__ == "__main__":

    app.run(debug=True)