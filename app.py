import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/home")
def home():
    items = mongo.db.items.find()
    return render_template("home.html", items=items)


@app.route("/get_items")
def get_items():
    items = list(mongo.db.items.find())
    return render_template("items.html", items=items)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checking previous usernames and emails
        existing_user = mongo.db.users.find_one(
            {'$or': [{"username": request.form.get("username").lower()},
                     {"email": request.form.get("email").lower()}]})

        if existing_user:
            flash("Username or email already in use")
            return redirect(url_for("register"))

        register = {
            "first_name": request.form.get("first_name").lower(),
            "last_name": request.form.get("last_name").lower(),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "email": request.form.get("email").lower(),
        }
        mongo.db.users.insert_one(register)

        # put the newuser into session cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successfull! Welcome to Restruction")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome back, {}".format(request.form.get("username")))
                return redirect(url_for("profile", username=session["user"]))

            else:
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        item = {
            "item_name": request.form.get("item_name"),
            "item_type": request.form.get("item_type"),
            "item_description": request.form.get("item_description"),
            "quantity": request.form.get("quantity"),
            "measurement_unit": request.form.get("measurement_unit"),
            "estimated_mass": request.form.get("estimated_mass"),
            "condition": request.form.get("condition"),
            "contact_name": request.form.get("contact_name"),
            "contact_email": request.form.get("contact_email"),
            "contact_phone": request.form.get("contact_phone"),
            "date_of_destruction": request.form.get("date_of_destruction"),
            "created_by": session["user"]
        }
        mongo.db.items.insert_one(item)
        flash("Task Successfully Added")
        return redirect(url_for("get_items"))

    item_type = mongo.db.item_type.find().sort("item_type", 1)
    return render_template("add_items.html", item_type=item_type)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
