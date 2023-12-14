from setup import db
from marshmallow import fields, INCLUDE, ValidationError
from datetime import datetime
from .base_schema import BaseSchema


class Pantry(db.Model):
    __tablename__ = 'pantries'
    pantry_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    name = db.Column(db.Text(), nullable=False)
    # This line connect the Pantry to the User model. This establish a bi-directional relationship between the User and Pantry models. 
    # This means we can easily access the related User object from a Pantry object, and vice versa.
    user = db.relationship('User', back_populates='pantry')
    items = db.relationship('PantryItem', back_populates='pantry')

class PantryItem(db.Model):
    __tablename__ = 'pantry_items'
    item_id = db.Column(db.Integer, primary_key=True)
    pantry_id = db.Column(db.Integer, db.ForeignKey('pantries.pantry_id'))
    item = db.Column(db.Text(), nullable=False)
    used_by_date = db.Column(db.Text(), nullable=False)  
    count = db.Column(db.Integer, nullable=False)
    run_out_time = db.Column(db.DateTime, nullable=True)
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
            raise ValidationError("Count must be an integer. Please ensure that the value is a number without any quotes or double quotes. For example, use 0 instead of '0'.")
        if count < 0:
            raise ValidationError("Count must be a non-negative integer.")

    # This staticmethod validates the item. It checks if the item is a string containing only alphabetic characters and spaces.
    @staticmethod
    def validate_item(item):
        if not all(word.isalpha() for word in item.split()):
            raise ValidationError("Item must be a string containing only alphabetic characters and spaces.")

    # This staticmethod validates the used_by_date. It checks if the date is in the format 'yyyy-mm-dd'
    @staticmethod
    def validate_used_by_date(date):
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValidationError("used_by_date must be a string in the format 'yyyy-mm-dd'")

# In some routes some fields are not required but in others they are,
# having a blanket schema would remove the approriate requirement fields and error handling message for each routes which I coded into the baseschema validation.

class PantryItemSchema(BaseSchema):
    # Serialization/deserialization and validation of the data. 
    # Might seem reduntant to define the type again as the type is define in the model for what is accepted input. 
    # However putting validating in the schema will allow for  validation error to be raise before the data is processed.
    item = fields.Str(required=True)
    used_by_date = fields.Str(required=True)
    count = fields.Int(required=True) 

    class Meta:
        unknown = INCLUDE
        fields = ("item", "used_by_date", "count")

class UpdatePantryItemSchema(BaseSchema):
    # the fields are not required since I want the client to decide what fields to update. They might only want to update one field only. 
    used_by_date = fields.Str()
    count = fields.Int()

    class Meta:
        unknown = INCLUDE
        fields = ("used_by_date", "count")