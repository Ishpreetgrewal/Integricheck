IntegriCheck is a file integrity checking system made using Python and Flask.
It helps you check whether a file has been changed or tampered with by using SHA-256 hashing.

How It Works
*You upload an original file
*The system creates and stores its hash (digital fingerprint)
*Later, you upload another copy of the file
*The system compares both hashes
*It tells you if the file is:
✅ Verified (no changes)
❌ Tampered (modified)
⚠️ Not found (no original record)

Features
*Upload original files
*Generate SHA-256 hash
*Verify file integrity
*Detect file tampering
*Dashboard to view stored files
*Stores data using SQLite database

Technologies Used
*Python
*Flask
*SQLite
*HTML
*CSS
*SHA-256 (hashing)

How to Run
pip install flask
python app.py

Then open:

http://127.0.0.1:5000
📌 Use Case

This project can be used for:

Checking file authenticity
Detecting file changes
Basic cybersecurity learning project
