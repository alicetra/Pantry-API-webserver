from dotenv import load_dotenv
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow

# Load environment variables
load_dotenv()

# Get the database password from environment variables
password = os.getenv('DB_PASSWORD')

# Initialize Flask app
app = Flask(__name__)

# Configure SQLAlchemy with the database URI. This uses the psycopg2 adapter for PostgreSQL.
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://flask_db_dev:{os.getenv("DB_PASSWORD")}@localhost/flask_db'

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)

# Initialize Bcrypt with the Flask app
bcrypt = Bcrypt(app)

# Set the secret key for the Flask app from environment variables
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.secret_key = os.getenv("SECRET_KEY") 

# Initialize Marshmallow with the Flask app
ma = Marshmallow(app)

