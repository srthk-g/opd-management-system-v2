from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "opd_secret_key_change_in_prod")

def get_db():
    conn = sqlite3.connect("hospital.db")
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/")
def home():
    db = get_db()
    beds = db.execute("SELECT available FROM beds").fetchone()[0]
    doctor_count = db.execute("SELECT COUNT(*) FROM doctors").fetchone()[0]
    doctors = db.execute(
        "SELECT id, name, specialty FROM doctors WHERE available=1"
    ).fetchall()
    db.close()
    return render_template("index.html", beds=beds, doctor_count=doctor_count, doctors=doctors)


# ── Patient ──────────────────────────────────────────────

@app.route("/register/patient", methods=["GET", "POST"])
def register_patient():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO patients VALUES (NULL, ?, ?, ?)",
            (request.form["name"], request.form["phone"], hash_password(request.form["password"]))
        )
        db.commit()
        db.close()
        return redirect(url_for("login_patient"))
    return render_template("register_patient.html")


@app.route("/login/patient", methods=["GET", "POST"])
def login_patient():
    error = None
    if request.method == "POST":
        db = get_db()
        user = db.execute(
            "SELECT * FROM patients WHERE phone=? AND password=?",
            (request.form["phone"], hash_password(request.form["password"]))
        ).fetchone()
        db.close()
        if user:
            session["patient_id"] = user[0]
            return redirect(url_for("patient_dashboard"))
        error = "Invalid phone number or password."
    return render_template("login_patient.html", error=error)


@app.route("/patient/dashboard")
def patient_dashboard():
    if "patient_id" not in session:
        return redirect(url_for("login_patient"))
    db = get_db()
    doctors = db.execute(
        "SELECT id, name, specialty FROM doctors WHERE available=1"
    ).fetchall()
    db.close()
    return render_template("patient_dashboard.html", doctors=doctors)


# ── Doctor ───────────────────────────────────────────────

@app.route("/register/doctor", methods=["GET", "POST"])
def register_doctor():
    if request.method == "POST":
        db = get_db()
        db.execute(
            "INSERT INTO doctors VALUES (NULL, ?, ?, ?, 1)",
            (request.form["name"], request.form["specialty"], hash_password(request.form["password"]))
        )
        db.commit()
        db.close()
        return redirect(url_for("login_doctor"))
    return render_template("register_doctor.html")


@app.route("/login/doctor", methods=["GET", "POST"])
def login_doctor():
    error = None
    if request.method == "POST":
        db = get_db()
        doctor = db.execute(
            "SELECT * FROM doctors WHERE name=? AND password=?",
            (request.form["name"], hash_password(request.form["password"]))
        ).fetchone()
        db.close()
        if doctor:
            session["doctor_id"] = doctor[0]
            return redirect(url_for("doctor_dashboard"))
        error = "Invalid name or password."
    return render_template("login_doctor.html", error=error)


@app.route("/doctor/dashboard")
def doctor_dashboard():
    if "doctor_id" not in session:
        return redirect(url_for("login_doctor"))
    db = get_db()
    appointments = db.execute(
        """SELECT p.name, a.date, a.time
           FROM appointments a
           JOIN patients p ON a.patient_id=p.id
           WHERE a.doctor_id=?""",
        (session["doctor_id"],)
    ).fetchall()
    db.close()
    return render_template("doctor_dashboard.html", appointments=appointments)


# ── Appointments ─────────────────────────────────────────

@app.route("/book", methods=["POST"])
def book():
    if "patient_id" not in session:
        return redirect(url_for("login_patient"))
    db = get_db()
    db.execute(
        "INSERT INTO appointments VALUES (NULL, ?, ?, ?, ?)",
        (session["patient_id"], request.form["doctor"], request.form["date"], request.form["time"])
    )
    db.commit()
    db.close()
    return render_template("confirmation.html")


# ── Inventory ────────────────────────────────────────────

@app.route("/login/inventory", methods=["GET", "POST"])
def login_inventory():
    error = None
    if request.method == "POST":
        manager_id = request.form.get("manager_id", "")
        password = request.form.get("password", "")
        if manager_id == "admin" and password == "admin123":
            session["inventory_manager"] = True
            return redirect(url_for("inventory"))
        error = "Invalid Manager ID or password."
    return render_template("inventory_manager.html", error=error)


@app.route("/inventory")
def inventory():
    if not session.get("inventory_manager"):
        return redirect(url_for("login_inventory"))
    return render_template("inventory.html")


# ── Logout ───────────────────────────────────────────────

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=False)
