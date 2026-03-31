from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "opd_secret_key"

def get_db():
    return sqlite3.connect("hospital.db")

@app.route("/")
def home():
    db = get_db()

    beds = db.execute(
        "SELECT available FROM beds"
    ).fetchone()[0]

    doctor_count = db.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]

    doctors = db.execute(
        "SELECT id, name, specialty FROM doctors WHERE available=1"
    ).fetchall()

    return render_template(
        "index.html",
        beds=beds,
        doctor_count=doctor_count,
        doctors=doctors
    )


@app.route("/register/patient", methods=["GET", "POST"])
def register_patient():
    if request.method == "POST":
        db = get_db()
        db.execute("INSERT INTO patients VALUES (NULL, ?, ?, ?)",
                   (request.form["name"], request.form["phone"], request.form["password"]))
        db.commit()
        return redirect("/login/patient")
    return render_template("register_patient.html")


@app.route("/login/patient", methods=["GET", "POST"])
def login_patient():
    if request.method == "POST":
        db = get_db()
        user = db.execute(
            "SELECT * FROM patients WHERE phone=? AND password=?",
            (request.form["phone"], request.form["password"])
        ).fetchone()

        if user:
            session["patient_id"] = user[0]
            return redirect("patient_dashboard.html")

    return render_template("login_patient.html")


@app.route("patient_dashboard.html ")
def patient_dashboard():
    if "patient_id" not in session:
        return redirect("login_patient.html")

    db = get_db()
    doctors = db.execute(
        "SELECT id, name, specialty FROM doctors WHERE available=1"
    ).fetchall()

    return render_template("patient_dashboard.html", doctors=doctors)


@app.route("register_doctor.html", methods=["GET", "POST"])
def register_doctor():
    if request.method == "POST":
        db = get_db()
        db.execute("INSERT INTO doctors VALUES (NULL, ?, ?, ?, 1)",
                   (request.form["name"], request.form["specialty"], request.form["password"]))
        db.commit()
        return redirect("login_doctor.html")

    return render_template("register_doctor.html")


# ✅ FIXED LOGIN
@app.route("login_doctor.html", methods=["GET", "POST"])
def login_doctor():
    if request.method == "POST":
        db = get_db()
        doctor = db.execute(
            "SELECT * FROM doctors WHERE name=? AND password=?",
            (request.form["name"], request.form["password"])
        ).fetchone()

        if doctor:
            session["doctor_id"] = doctor[0]
            return redirect(url_for("doctor_dashboard"))  # ✅ FIXED

    return render_template("login_doctor.html")


@app.route("/doctor/dashboard")
def doctor_dashboard():
    if "doctor_id" not in session:
        return redirect("login_doctor.html")

    db = get_db()
    appointments = db.execute(
        """SELECT p.name, a.date, a.time 
           FROM appointments a 
           JOIN patients p ON a.patient_id=p.id 
           WHERE a.doctor_id=?""",
        (session["doctor_id"],)
    ).fetchall()

    return render_template("doctor_dashboard.html", appointments=appointments)


@app.route("/book", methods=["POST"])
def book():
    if "patient_id" not in session:
        return redirect("login_patient.html")

    db = get_db()
    db.execute("INSERT INTO appointments VALUES (NULL, ?, ?, ?, ?)",
               (session["patient_id"], request.form["doctor"], request.form["date"], request.form["time"]))
    db.commit()

    return redirect("patient_dashboard.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)