from setup import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re

class Pantry(db.Model):
    __tablename__ = 'pantries'
    pantry_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    name = db.Column(db.Text(), nullable=False)
    #This line connect the Pantry to the User model. This establish a bi-directional relationship between the User and Pantry models. 
    #This means we  can easily access the related User object from a Pantry object, and vice versa.
    user = db.relationship('User', back_populates='pantry')
    #This line connect the Pantry to the PantryItem  model. This establish a bi-directional relationship between the Pantry and PantryItem models. 
    #This means we  can easily access the related Pantryitem object from a Pantry object, and vice versa.
    items = db.relationship('PantryItem', back_populates='pantry')

class PantryItem(db.Model):
    __tablename__ = 'pantry_items'
    item_id = db.Column(db.Integer, primary_key=True)
    pantry_id = db.Column(db.Integer, db.ForeignKey('pantries.pantry_id'))
    item = db.Column(db.Text(), nullable=False)
    used_by_date = db.Column(db.Text(), nullable=False)  
    count = db.Column(db.Integer, nullable=False)
    run_out_time = db.Column(db.DateTime, nullable=True)
    #This line connect the Pantry to the PantryItem  model. This establish a bi-directional relationship between the Pantry and PantryItem models. 
    #This means we  can easily access the related Pantryitem object from a Pantry object, and vice versa.
    pantry = db.relationship('Pantry', back_populates='items')

    # Benefits of using static methods for validation:
    # 1. Flexibility: Can be called without creating an instance of the class.
    # 2. Consistency: Ensures the same validation rules are applied everywhere.
    # 3. Reusability: Can be called from anywhere in the code.
    # 4. JSON Compatibility: Works well with JSON data, allowing validation before object creation.

    # This staticmethod validates the count. It checks if the count is an integer and non-negative.
    @staticmethod
    def validate_count(count):
        if not isinstance(count, int):
            raise ValidationError("Count must be an integer. Please ensure that the value is a number without any quotes or double quotes. For example, use 0 instead of '0' or \"0\".")
        if count < 0:
            raise ValidationError("Count must be a non-negative integer.")

    # This staticmethod validates the item. It checks if the item is a string containing only alphabetic characters and spaces.
    @staticmethod
    def validate_item(item):
        if not all(word.isalpha() for word in item.split()):
            raise ValidationError("Item must be a string containing only alphabetic characters and spaces.")

     # This staticmethod validates the used_by_date. It checks if the date is in the format 'dd-mm-yyyy'
    @staticmethod
    def validate_used_by_date(date):
        try:
            datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            raise ValidationError("used_by_date must be a string in the format 'dd-mm-yyyy'")

