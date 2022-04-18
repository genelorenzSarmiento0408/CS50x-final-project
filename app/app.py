import os

from flask import Flask, request, session, render_template, redirect, url_for, send_from_directory, make_response
from flask_session import Session
from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
from app.helpers.helpers import login_required, faculty_required
app = Flask(__name__)

# Ensure templates are autoreloaded
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Configure cs50 Library to use SQLite database
db = SQL("sqlite:///app/school.db")
print("Success in connecting the database")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def apology(m, code):
    return render_template("apology.html", error=m), code

# https://stackoverflow.com/questions/19859282/check-if-a-string-contains-a-number
def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')


@app.route('/sw.js')
def service_worker():
    response = make_response(send_from_directory('static', 'sw.js'))
    response.headers['Cache-Control'] = 'no-cache'
    return response
# Create custom error: https://flask.palletsprojects.com/en/2.1.x/quickstart/#redirects-and-errors
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route("/", methods=["GET"])
@login_required
def index():
    if session.get("user_id") is None:
        # https://flask.palletsprojects.com/en/2.1.x/quickstart/#redirects-and-errors
        return redirect(url_for('login'))

    school_role = session["school_role"]
    id = session["user_id"]
    username = db.execute("SELECT username FROM users WHERE id = ?", id)[0]['username']
    rows = None
    # If the role is teacher, get all the courses they teach
    if school_role == "Teacher" or school_role == "Principal":
        first_name = db.execute("SELECT first_name FROM users WHERE id = ?", session["user_id"])[0]["first_name"]
        last_name = db.execute("SELECT last_name FROM users WHERE id = ?", session["user_id"])[0]["last_name"]
        name = f"{first_name} {last_name}"
        rows = db.execute("SELECT * FROM subjects WHERE teacher = ?", name)
        print(rows)
    else:
        grade = db.execute("SELECT grade FROM users WHERE id = ?", id)[0]['grade']
        rows = db.execute("SELECT * FROM subjects WHERE grade = ?", grade)
        print(rows)

    return render_template("index.html", name=username, role=school_role, rows=rows)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register the user and redirect to their corresponding class/es"""
    school_roles = [
        "Teacher",
        "Student",
        "Principal",
        "Others"
    ]
    # If the request is POST, then process it
    if request.method == "POST":

        # Get the input and store it in a variable
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")
        grade = request.form.get("grade")
        section = request.form.get("section")
        school_role = request.form.get("school_role")

        # Credits to Veinhugain#0195 in Scrimba's and helis#6936 in CS50's Discord
        fields = [
            first_name,
            last_name,
            username,
            password,
            confirm_password,
            school_role
        ]

        # If the role is not present
        if not school_role:
            return apology("The school role SHOULD NOT be blank", 400)

        # If the school role is Student, the you should add grade and section
        elif school_role.capitalize() == "Student":
            fields.append(grade)
            fields.append(section)

        # If the any of input is not present return an apology
        elif False in fields:
            return apology("Form should NOT be left blank", 400)

        find_username = db.execute("SELECT * FROM users WHERE username = ?", username)

        # If password and confirm_password do not match, return an apology
        if password != confirm_password:
            return apology("Password and confirm password should match", 400)

        # If it finds username (in registering), return an error
        elif find_username:
            return apology("Username already exists", 400)

        # If the faculty type is not valid then
        elif not school_role.capitalize() in school_roles:
            return apology("School role is invalid", 400)

        # If the grade or section is absent and the role is an teacher
        elif school_role.capitalize() == "Teacher" or "Principal":
            if not grade or not section:
                db.execute("INSERT INTO users (first_name, last_name, username, password, school_role) VALUES(?, ?, ?, ?, ?)",
                first_name, last_name, username, generate_password_hash(password), school_role
                )
                row = db.execute("SELECT * FROM users WHERE username = ?", username)
                # Remember which user has logged in
                session["user_id"] = row[0]["id"]
                # Remember school_role
                session["school_role"] = row[0]["school_role"]
                return redirect("/")

        # If the grade is a number, convert it, if it is more than 12 it should be invalid
        elif grade.isdigit():
            if int(grade) > 12:
                return apology("Invalid number. The grade SHOULD be 1-12", 400)

        elif not grade.isdigit():
            return apology("Invalid number. The grade SHOULD be 1-12",400)

        db.execute("INSERT INTO users (first_name, last_name, username, password, grade, section, school_role) VALUES(?, ?, ?, ?, ?, ?, ?)",
        first_name, last_name, username, generate_password_hash(password), grade, section, school_role
        )

        row = db.execute("SELECT * FROM users WHERE username = ?", username)
        # Remember which user has logged in
        session["user_id"] = row[0]["id"]
        # Remember school_role
        session["school_role"] = row[0]["school_role"]

        # Redirect user to home page
        return redirect("/")
    return render_template("register.html", roles=school_roles)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Remember what type of user is it
        session["school_role"] = rows[0]["school_role"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/add_subject", methods=["POST", "GET"])
@login_required
@faculty_required
def add_subject():
    if request.method == "POST":
        first_name = db.execute("SELECT first_name FROM users WHERE id = ?", session["user_id"])[0]["first_name"]
        last_name = db.execute("SELECT last_name FROM users WHERE id = ?", session["user_id"])[0]["last_name"]
        name = f"{first_name} {last_name}"
        subject = request.form.get("subject")
        grade = request.form.get("grade")
        section = request.form.get("section")
        link = request.form.get("link")
        time = request.form.get("time")
        if not subject or not grade or not section or not time:
            return apology("Subject, grade, and/or section should not be blank", 400)

        elif grade.isdigit():
            if int(grade) > 12:
                return apology("Invalid number. The grade SHOULD be 1-12", 400)

        elif not grade.isdigit():
            return apology("Invalid number. The grade SHOULD be 1-12",400)

        elif not has_numbers(time):
            return apology("Time should have a number", 400)
        print(link)
        if link:
            db.execute("INSERT INTO subjects (subject, grade, section, time, link, teacher) VALUES (?, ?, ?, ?, ?, ?)",
            subject, grade, section, time, link, name)
            print("Success")
            return redirect("/")

        db.execute("INSERT INTO subjects (subject, grade, section, time, teacher) VALUES (?, ?, ?, ?, ?)",
        subject, grade, section, time, name )
        return redirect("/")
    return render_template("add_subject.html")



@app.route("/find_class", methods=["POST", "GET"])
def find_class():
    if request.method == "POST":
        subject = request.form.get("subject")
        grade = request.form.get("grade")
        section = request.form.get("section")

        # If the user has logged in collect all information
        if "user_id" in session :
            rows = db.execute("SELECT * FROM subjects WHERE subject LIKE ? AND grade LIKE ? AND section LIKE ?",
            subject, grade, section
            )
            print(rows)
            return render_template("subject.html", rows=rows)

        else:
            rows = db.execute("SELECT subject, grade, time, section, teacher FROM subjects WHERE subject LIKE ? AND grade LIKE ? AND section LIKE ?",
            subject, grade, section,
            )
            print(rows)
            return render_template("subject.html", rows=rows)

    return render_template("find_class.html")



