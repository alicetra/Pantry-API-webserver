from flask import Blueprint
from setup import db,app
from models.user import User
from models.pantry import Pantry, PantryItem
from models.authorization import RevokedToken

# Create a new blueprint named 'db'. This allows us to organize Flask application into smaller and reusable applications.
db_commands = Blueprint('db', __name__)

# Register a new command 'create' that can be run in the Flask application's command line interface (CLI).
@app.cli.command('create')
def create_db():
    # 'app_context()' is a context manager that binds the application instance to the current context.
    # This is necessary because Flask uses a concept of application contexts and request contexts.
    # Some operations (like database operations) can only be performed within an application context.
    with app.app_context():
        # 'create_all()' is a method that creates all tables defined in our SQLAlchemy models.
        db.create_all()
        # Print a success message to the console.
        print("Tables created successfully")