from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))

    author = db.Column(db.String(200))

    body = db.Column(db.Text)

    image_url = db.Column(db.String(500))