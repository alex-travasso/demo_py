from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_oidc import OpenIDConnect
import MySQLdb.cursors
import re, json, logging

app = Flask(__name__)


# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = "brbrbrb_thisisdemokey"

# Enter your database connection details below
app.config["MYSQL_HOST"] = "db-demo.censbyvrlwuv.us-east-1.rds.amazonaws.com"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ".Test1234-"
app.config["MYSQL_DB"] = "pythonlogin"

# Intialize MySQL
mysql = MySQL(app)

# OIDC conf
app.config.update(
    {
        "SECRET_KEY": "HXhuNd9xBamc8ORvP3PUGyODVfFThX8_yPfgqohOXio",
        "TESTING": True,
        "DEBUG": True,
        "OIDC_CLIENT_SECRETS": "client_secrets_MID.json",
        "OIDC_SCOPES": ["openid", "phone", "profile"],
        "OIDC_INTROSPECTION_AUTH_METHOD": "client_secret_post",
        "OIDC_ID_TOKEN_COOKIE_SECURE": False,
        "OIDC_REQUIRE_VERIFIED_EMAIL": False,
        "OIDC_OPENID_REALM": "https://mid-dev.com/oidc_callback",
        "OIDC_VALID_ISSUERS": "https://openid.mobileid.ch",
    }
)
oidc = OpenIDConnect(app)

# http://34.199.8.76:5000/
@app.route("/")
def index():
    return render_template("home.html")


# http://34.199.8.76:5000/
@app.route("/select")
def select():
    if "loggedin" in session:
        # User is loggedin show them the home page
        return redirect(url_for("profile"))
    else:
        return render_template("select.html")


# http://34.199.8.76:5000/demo/home/
@app.route("/home")
def home():
    return render_template("home.html")


# http://localhost:5000/python/logout - this will be the logout page
@app.route("/logout")
def logout():
    # Remove session data, this will log the user out
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    session["loggedin"] = False
    # Redirect to login page
    return redirect(url_for("select"))


@app.route("/login", methods=["GET", "POST"])
def login():
    # Check if user is loggedin
    if "loggedin" in session:
        # User is loggedin show them the home page
        return redirect(url_for("profile"))

    # Output message if something goes wrong...
    msg = ""
    # Check if "username" and "password" POST requests exist (user submitted form)
    if (
        request.method == "POST"
        and "username" in request.form
        and "password" in request.form
    ):
        # Create variables for easy access
        username = request.form["username"]
        password = request.form["password"]
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            "SELECT * FROM accounts WHERE username = %s AND password = %s",
            (
                username,
                password,
            ),
        )
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session["loggedin"] = True
            session["id"] = account["id"]
            session["username"] = account["username"]
            session["login_method"] = "basic"

            # Redirect to home page
            return redirect(url_for("profile"))
        else:
            # Account doesnt exist or username/password incorrect
            msg = "Incorrect username/password!"
    # Show the login form with message (if any)
    return render_template("index.html", msg=msg)


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route("/profile")
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        if session["loggedin"]:
            return render_template("profile.html")
        else:
            return render_template("select.html")
    else:
        return render_template("select.html")


@app.route("/login_oidc", methods=["GET", "POST"])
def login_oidc():
    if oidc.user_loggedin:
        return (
            'Hello, %s, <a href="/private">See private</a> '
            '<a href="/logout">Log out</a>'
        ) % oidc.user_getfield("usrname")
    else:
        return 'Welcome anonymous, <a href="/private">Log in</a>'


@app.route("/private")
@oidc.require_login
def hello_me():
    session["loggedin"] = True
    session["login_method"] = "OIDC - Mobile ID"
    session["username"] = oidc.user_getfield("name")
    session["sub"] = oidc.user_getfield("sub")
    print(session['sub'])
    return render_template("profile.html")
