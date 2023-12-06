from setup import db, bcrypt
from flask_bcrypt import Bcrypt
from sqlalchemy import event
from marshmallow import ValidationError
import re
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

    @staticmethod
    def validate_password(password):
        if len(password) < 8:
            raise ValidationError("Password must contain a minimum of eight characters.")
        elif not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        elif not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        elif not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number.")
        elif not re.search(r'\W', password):
            raise ValidationError("Password must contain at least one special character.")
        #This line prevent a password with spaces in the at any point in of the string to be accepted as it would still pass the special character check without this line.
        #Decided to keep this as a seperate requirement instead of changing the special character code to make the requirement of a password explicit.
        elif ' ' in password:
            raise ValidationError("Password must not contain spaces.")

    @staticmethod
    def validate_username(username):
        if not re.match('^[a-zA-Z0-9]*$', username):
            raise ValidationError("Username can only contain alphanumeric characters. Special character and spaces are not accepted.")

    @staticmethod
    def validate_email(email):
        if len(email) > 320:
            raise ValidationError("Email must not exceed 320 characters.")
        elif not re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
            raise ValidationError("Invalid email format. Please ensure your email is in the format 'example@example.com'.")
        
        # Normalize the email address by converting the domain part to lowercase
        email_username, email_domain = email.rsplit('@', 1)
        email = '@'.join([email_username, email_domain.lower()])
        
        return email


    @staticmethod
    def validate_security_answer(security_answer):
        if not security_answer.isalpha():
            raise ValidationError("Security answer must only contain alphabetic characters. Special character and spaces are not accepted. Please note that answer will be case-insentitive")

#This event listener decorator means that the function that follows will be executed after a new User record is inserted into the database. Since I want all users to have one pantry it made sense to automatically create one as a user is created their database is too.
@event.listens_for(User, 'after_insert')
#connection is the active database connection, and target is the actual User table that was just inserted. SQLAlchemy will still pass three arguments when the after_insert event is triggered hence why by convention I used _ as a placeholder for a parameter that is not used/needed.
def create_pantry(_, connection, target):
    #This line creates a new Pantry object associated with the newly created User. The name is set to a string that includes the username of the User
    pantry = Pantry(user_id=target.id, name=f"{target.username}'s Pantry")
    db.session.add(pantry)