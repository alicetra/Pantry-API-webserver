from dotenv import load_dotenv
import os
from flask import Flask,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow




load_dotenv()

password = os.getenv('DB_PASSWORD')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://flask_db_dev:{os.getenv("DB_PASSWORD")}@localhost/flask_db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.secret_key = os.getenv("SECRET_KEY") 
ma = Marshmallow(app)

