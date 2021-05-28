import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

# below is the config for MongoDB
app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)

# config for the cloudinary API used to store the item images
cloudinary.config(
    cloud_name=os.environ.get("CLOUD_NAME"),
    api_key=os.environ.get("API_KEY"),
    api_secret=os.environ.get("API_SECRET")
)


@app.route("/")
@app.route("/home")
def home():
    """
    This is the home route. shows the 10 most recent posted items.
    """
    items = mongo.db.items.find().sort("_id", -1).limit(10)
    return render_template("home.html", items=items)


@app.route("/get_items")
def get_items():
    """
    This is the route to get all posted items onto the items.html page.
    """
    items = list(mongo.db.items.find())
    return render_template("items.html", items=items)


@app.route("/search", methods=["GET", "POST"])
def search():
    """
    This is the search route for the items.html page.
    """
    query = request.form.get("query")
    items = list(mongo.db.items.find({"$text": {"$search": query}}))
    return render_template("items.html", items=items)


@app.route("/user_items")
def user_items():
    """
    This is the route to get all items posted by the session user.
    """
    items = list(mongo.db.items.find(
        {"created_by": session["user"]}))
    return render_template("user_items.html", items=items)


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    This is the route to check for an existing user and register a new one
    """
    if request.method == "POST":
        # checking for previous usernames or emails
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

        # put the new user into session cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful! Welcome to Restruction")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    This is the login route.
    """
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
    """
    This is the profile page route.
    """
    user = mongo.db.users.find_one(
        {"username": session["user"]})

    if session["user"]:
        return render_template("profile.html", user=user)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """
    This is the logout route.
    """
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    """
    This is the route to add items to the database.
    """
    if request.method == "POST":
        photo = request.files['photo_url']
        photo_upload = cloudinary.uploader.upload(photo)
        item = {
            "item_name": request.form.get("item_name"),
            "item_type": request.form.get("item_type"),
            "item_description": request.form.get("item_description"),
            "quantity": request.form.get("quantity"),
            "dimensions": request.form.get("dimensions"),
            "estimated_mass": request.form.get("estimated_mass"),
            "condition": request.form.get("condition"),
            "contact_name": request.form.get("contact_name"),
            "contact_email": request.form.get("contact_email"),
            "contact_phone": request.form.get("contact_phone"),
            "date_of_destruction": request.form.get("date_of_destruction"),
            "item_location": request.form.get("item_location"),
            "photo_url": photo_upload["secure_url"],
            "created_by": session["user"]
        }
        mongo.db.items.insert_one(item)
        flash("Item Successfully Added")
        return redirect(url_for("get_items"))

    item_type = mongo.db.item_type.find().sort("item_type", 1)
    return render_template("add_items.html", item_type=item_type)


@app.route("/edit_item/<item_id>", methods=["GET", "POST"])
def edit_item(item_id):
    """
    This is the route edit items. Both Get and Post methods so the form is
    preloaded with the existing text.
    """
    if request.method == "POST":
        mongo.db.items.update_one(
            {"_id": ObjectId(item_id)},
            {"$set":
                {
                    "item_name": request.form.get("item_name"),
                    "item_type": request.form.get("item_type"),
                    "item_description": request.form.get("item_description"),
                    "quantity": request.form.get("quantity"),
                    "dimensions": request.form.get("dimensions"),
                    "estimated_mass":
                        request.form.get("estimated_mass"),
                    "condition": request.form.get("condition"),
                    "contact_name": request.form.get("contact_name"),
                    "contact_email": request.form.get("contact_email"),
                    "contact_phone": request.form.get("contact_phone"),
                    "date_of_destruction":
                        request.form.get("date_of_destruction"),
                    "item_location": request.form.get("item_location"),
                    "created_by": session["user"]
                }
             })
        flash("Item Successfully Updated")

    item = mongo.db.items.find_one({"_id": ObjectId(item_id)})
    item_type = mongo.db.item_type.find().sort("item_type", 1)
    return render_template("edit_item.html", item=item, item_type=item_type)


@app.route("/delete_item/<item_id>")
def delete_item(item_id):
    """
    This is the route to delete items.
    """
    mongo.db.items.remove({"_id": ObjectId(item_id)})
    flash("Item Successfully Deleted")
    return redirect(url_for("user_items"))


@app.route("/get_item_type")
def get_item_type():
    """
    This is the route to get item_type as that is in a seperate collection so
    had to be seperate to the normal get items route.
    """
    item_type = list(mongo.db.item_type.find().sort("item_type", 1))
    return render_template("item_type.html", item_type=item_type)


@app.route("/add_item_type", methods=["GET", "POST"])
def add_item_type():
    """
    This is the route to add item_type and is only available to the admin.
    """
    if request.method == "POST":
        item_type = {
            "item_type": request.form.get("item_type")
        }
        mongo.db.item_type.insert_one(item_type)
        flash("New Item Type Added")
        return redirect(url_for("get_item_type"))

    return render_template("add_item_type.html")


@app.route("/edit_item_type/<item_type_id>", methods=["GET", "POST"])
def edit_item_type(item_type_id):
    """
    This is the route to edit item_type and is only available to the admin.
    """
    if request.method == "POST":
        submit = {
            "item_type": request.form.get("item_type")
        }
        mongo.db.item_type.update({"_id": ObjectId(item_type_id)}, submit)
        flash("Item Type successfully updated")
        return redirect(url_for("get_item_type"))

    item_type = mongo.db.item_type.find_one({"_id": ObjectId(item_type_id)})
    return render_template("edit_item_type.html", item_type=item_type)


@app.route("/delete_item_type/<item_type_id>")
def delete_item_type(item_type_id):
    """
    This is the route to delete item_type and is only available to the admin.
    """
    mongo.db.item_type.remove({"_id": ObjectId(item_type_id)})
    flash("Item Type successfully deleted")
    return redirect(url_for("get_item_type"))


@app.route("/edit_users/<users_id>", methods=["GET", "POST"])
def edit_users(users_id):
    """
    This is the route to edit a user and only allows users to edit their name 
    and email.
    """
    if request.method == "POST":
        mongo.db.users.update_one(
            {"_id": ObjectId(users_id)},
            {"$set":
                {
                    "first_name": request.form.get("first_name"),
                    "last_name": request.form.get("last_name"),
                    "email": request.form.get("email")
                }
             })
        flash("User Successfully Updated")

    user = mongo.db.users.find_one({"_id": ObjectId(users_id)})
    return render_template("profile.html", user=user)


@app.errorhandler(404)
def page_not_found(error):
    """
    This is the route to send 404 errors to the 404.html template.
    """
    return render_template('404.html'), 404


@app.errorhandler(500)
def something_wrong(error):
    """
    This is the route to send 500 errors to the 500.html template.
    """
    return render_template('500.html'), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
