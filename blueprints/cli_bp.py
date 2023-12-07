from flask import Blueprint
from setup import db,app
from models.user import User
from models.pantry import Pantry, PantryItem
from models.authorization import RevokedToken

db_commands = Blueprint('db', __name__)

@app.cli.command('create')
def create_db():
    with app.app_context():
        db.create_all()
        print("Tables created successfully")