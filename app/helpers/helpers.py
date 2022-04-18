from flask import redirect, session, render_template, url_for
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            print(url_for("login"))
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def faculty_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(session.get("school_role"))
        if session.get("school_role") != "Teacher":
            if session.get("school_role") != "Principal":
                return render_template("apology.html", error="Action forbidden"), 403
        return f(*args, **kwargs)
    return decorated_function
