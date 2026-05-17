from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "ganpati_secret"

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# TABLES (UNCHANGED)
cursor.execute("""
CREATE TABLE IF NOT EXISTS people(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    amount INTEGER,
    category TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item TEXT,
    amount INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS visitors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

conn.commit()


# ================= ROOT =================
@app.route("/")
def root():
    if "user" in session:
        return redirect("/home")
    return redirect("/login")


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]

        if password == "04052022":
            session["user"] = name
            session["role"] = "admin"

        elif password == "262378":
            session["user"] = name
            session["role"] = "viewer"
        else:
            return "Wrong password"

        cursor.execute("INSERT OR IGNORE INTO visitors(name) VALUES (?)", (name,))
        conn.commit()

        return redirect("/home")

    return render_template("login.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ================= HOME (READ + ADMIN WRITE ONLY) =================
@app.route("/home", methods=["GET", "POST"])
def home():

    if "user" not in session:
        return redirect("/login")

    # ❗ ONLY ADMIN CAN ADD DATA
    if request.method == "POST":
        if session.get("role") != "admin":
            return "VIEW ONLY MODE ❌"

        name = request.form["name"]
        amount = request.form["amount"]
        category = request.form["category"]

        cursor.execute(
            "INSERT INTO people(name, amount, category) VALUES (?, ?, ?)",
            (name, amount, category)
        )
        conn.commit()

        return redirect("/home")

    cursor.execute("SELECT id, name, amount, category FROM people")
    people = cursor.fetchall()

    cursor.execute("SELECT id, item, amount FROM expenses")
    expenses = cursor.fetchall()

    total = boys = area = outside = 0

    for p in people:
        amt = int(p[2])
        total += amt

        if p[3] == "Boys":
            boys += amt
        elif p[3] == "Area":
            area += amt
        elif p[3] == "Outside":
            outside += amt

    expense_total = sum(int(e[2]) for e in expenses)
    remaining = total - expense_total

    return render_template(
        "index.html",
        people=people,
        expenses=expenses,
        total=total,
        boys_total=boys,
        area_total=area,
        outside_total=outside,
        expense_total=expense_total,
        remaining=remaining,
        user=session.get("user"),
        role=session.get("role")
    )


# ================= EXPENSE (ADMIN ONLY) =================
@app.route("/expense", methods=["POST"])
def expense():
    if session.get("role") != "admin":
        return "VIEW ONLY MODE ❌"

    item = request.form["item"]
    amount = request.form["amount"]

    cursor.execute("INSERT INTO expenses(item, amount) VALUES (?, ?)", (item, amount))
    conn.commit()

    return redirect("/home")


# ================= DELETE COLLECTION (ADMIN ONLY) =================
@app.route("/delete/<int:id>")
def delete(id):
    if session.get("role") != "admin":
        return "VIEW ONLY MODE ❌"

    cursor.execute("DELETE FROM people WHERE id=?", (id,))
    conn.commit()
    return redirect("/home")


# ================= DELETE EXPENSE (ADMIN ONLY) =================
@app.route("/delete_expense/<int:id>")
def delete_expense(id):
    if session.get("role") != "admin":
        return "VIEW ONLY MODE ❌"

    cursor.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    return redirect("/home")


# ================= VISITORS (READ ONLY) =================
@app.route("/visitors")
def visitors():
    if "user" not in session:
        return redirect("/login")

    cursor.execute("""
        SELECT name
        FROM visitors
        GROUP BY name
        ORDER BY MAX(id) DESC
    """)

    data = cursor.fetchall()

    return render_template("visitors.html", visitors=data)


if __name__ == "__main__":
    app.run(debug=True)