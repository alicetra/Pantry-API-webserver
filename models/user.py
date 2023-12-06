from setup import db, bcrypt
from flask_bcrypt import Bcrypt
from sqlalchemy import event
from marshmallow import ValidationError
from models.pantry import Pantry


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text(), unique=True, nullable=False) 
    password_hash = db.Column(db.Text(), nullable=False)
    email = db.Column(db.String(320), unique=True, nullable=False) 
    security_question = db.Column(db.Text(), nullable=False)
    security_answer = db.Column(db.Text(), nullable=False)  
    pantry = db.relationship('Pantry', back_populates='user', uselist=False)

    #This line is using the bcrypt library’s generate_password_hash function to create a hashed version of the password.
    #The hashed password is then decoded from bytes to a UTF-8 string and stored in the password_hash attribute.
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    #This line is using the bcrypt library’s check_password_hash function. It takes two parameters: the hashed password and the password to check.
    #It compares the hashed version of the password to check with the stored hashed password. If they match, it returns True.
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def set_security_answer(self, security_answer):
        self.security_answer = bcrypt.generate_password_hash(security_answer).decode('utf-8')

    def check_security_answer(self, security_answer):
        return bcrypt.check_password_hash(self.security_answer, security_answer)

    def __repr__(self):
        return '<User %r>' % self.username
