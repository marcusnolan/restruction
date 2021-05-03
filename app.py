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
@app.route("/get_items")
def get_items():
    items = mongo.db.items.find()
    return render_template("items.html", items=items)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # checking previous usernames
        existing_user = mongo.db.users.find(
            {"username": request.form.get("username").lower()},
            {"email": request.form.get("email").lower()})


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

    return render_template("register.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)