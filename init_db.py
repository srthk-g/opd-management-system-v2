import sqlite3

conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
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

conn.commit()
conn.close()

print("✅ Database created successfully")
