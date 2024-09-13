from flask import Flask
from models import db

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)

with app.app_context():
    db.create_all()