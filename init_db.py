import sqlite3
import hashlib
import os

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

db_path = "hospital.db"

# Remove old DB if exists so we start fresh
if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialty TEXT,
    password TEXT,
    available INTEGER
)
""")

cursor.execute("""
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    date TEXT,
    time TEXT
)
""")

cursor.execute("""
CREATE TABLE beds (
    total INTEGER,
    available INTEGER
)
""")

cursor.execute("INSERT INTO beds VALUES (150, 120)")

# Seed a sample doctor so login works out of the box
cursor.execute("INSERT INTO doctors VALUES (NULL, 'Dr. Sharma', 'General Medicine', ?, 1)",
               (hash_password("doctor123"),))
cursor.execute("INSERT INTO doctors VALUES (NULL, 'Dr. Patel', 'Cardiology', ?, 1)",
               (hash_password("doctor123"),))

conn.commit()
conn.close()
print("Database created successfully")
