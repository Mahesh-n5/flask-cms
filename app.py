from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from azure.storage.blob import BlobServiceClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import uuid
import logging
import os
from datetime import datetime
from config import Config

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()

# ---------------------------
# Flask App Setup
# ---------------------------
app = Flask(__name__)
app.config.from_object(Config)

app.secret_key = app.config["SECRET_KEY"]

logging.basicConfig(level=logging.INFO)

# ---------------------------
# Database
# ---------------------------
db = SQLAlchemy(app)

# ---------------------------
# Azure Blob Storage
# ---------------------------
blob_service_client = None
container_client = None

try:
    connection_string = app.config.get("AZURE_STORAGE_CONNECTION_STRING")

    if connection_string:
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(
            app.config.get("CONTAINER_NAME")
        )
        logging.info("Azure Blob Storage connected successfully")
    else:
        logging.warning("Azure Storage connection string not found")

except Exception as e:
    logging.error(f"Azure Blob Storage connection failed: {e}")

# ---------------------------
# Database Models
# ---------------------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(75), nullable=False)
    body = db.Column(db.String(800), nullable=False)
    image_path = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

# ---------------------------
# Create Tables
# ---------------------------
try:
    with app.app_context():
        db.create_all()
        logging.info("Database tables verified/created successfully")
except Exception as e:
    logging.error(f"Database initialization error: {e}")

# ---------------------------
# Home Page
# ---------------------------
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        posts = Post.query.order_by(Post.timestamp.desc()).all()
    except Exception as e:
        logging.error(f"Error fetching posts: {e}")
        posts = []

    return render_template("index.html", posts=posts)

# ---------------------------
# Register
# ---------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = generate_password_hash(request.form.get("password"))

        try:
            user = User(username=username, password_hash=password)
            db.session.add(user)
            db.session.commit()

            logging.info("User registered successfully")
            return redirect(url_for("login"))

        except Exception as e:
            logging.error(f"Registration error: {e}")
            return "Registration failed"

    return render_template("register.html")

# ---------------------------
# Login
# ---------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password_hash, password):
                session["user_id"] = user.id
                session["username"] = user.username
                return redirect(url_for("index"))

            return "Invalid username or password"

        except Exception as e:
            logging.error(f"Login error: {e}")
            return "Login failed"

    return render_template("login.html")

# ---------------------------
# Logout
# ---------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------------------------
# Create Post
# ---------------------------
@app.route("/create_post", methods=["POST"])
def create_post():
    if "user_id" not in session:
        return redirect(url_for("login"))

    title = request.form.get("title")
    author = request.form.get("author")
    body = request.form.get("content")
    image = request.files.get("image")

    image_path = None

    if image and image.filename != "" and container_client:
        filename = str(uuid.uuid4()) + "_" + image.filename

        try:
            blob_client = container_client.get_blob_client(filename)
            blob_client.upload_blob(image, overwrite=True)

            image_path = filename
            logging.info("Image uploaded to Azure Blob")

        except Exception as e:
            logging.error(f"Image upload error: {e}")

    try:
        post = Post(
            title=title,
            author=author,
            body=body,
            image_path=image_path,
            user_id=session["user_id"]
        )

        db.session.add(post)
        db.session.commit()

        logging.info("Post created successfully")

    except Exception as e:
        logging.error(f"Post creation error: {e}")

    return redirect(url_for("index"))

# ---------------------------
# Health Check (Azure)
# ---------------------------
@app.route("/health")
def health():
    return "OK"

# ---------------------------
# Gunicorn Entry Point
# ---------------------------
application = app

# ---------------------------
# Local Run
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)