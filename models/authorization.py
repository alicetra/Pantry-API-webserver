from marshmallow import fields, INCLUDE
from setup import db
from .base_schema import BaseSchema



#This RevokedToken class is used for when a token is revoked,its unique identifier ‘jti’ is stored in the ‘revoked_tokens’ table.
class RevokedToken(db.Model):
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        # Add the current instance of the RevokedToken class to the database session
        db.session.add(self)
        # Commit (save) the changes in the session to the database
        db.session.commit()

    @classmethod
    # Query the database for a token with the provided jti
    def is_jti_blacklisted(cls, jti):
        # .scalar() returns the result of the query as a Python object, or None if there are no results
        query = cls.query.filter_by(jti=jti).scalar()
         # Return True if a token was found (i.e., the token is blacklisted), and False otherwise
        return bool(query)

#In some routes some fields are not required but in others they are,
#having a blanket schema would remove the approriate requirement fields and error handling message for each routes which I coded into the baseschema validation.

class UserSchema(BaseSchema):
     #Serialization/deserialization and validation of the data. Might seem reduntant to define the type again as the type is define in the model for what is accepted input.
     #However putting validating in the schema will allow for validation error to be raise before the data is processed.
    username = fields.Str(required=True)
    password = fields.Str(required=True)

    class Meta:
        #This line allows for unknown fields and my custom validation in BaseSchema to takes over, providing my specific error message. 
        #Else a generic message will be provided as " "Unknown field."
        unknown = INCLUDE 
        fields = ("username", "password")

class LoginSchema(UserSchema):
    pass

class RegisterSchema(UserSchema): 
    email = fields.Str(required=True) 
    security_answer = fields.Str(required=True)

    class Meta:
        unknown = INCLUDE
        # UserSchema.Meta.fields refers to the 'fields' attribute in the Meta class inside UserSchema. 
        # It's a tuple containing the field names ("username", "password") defined in UserSchema.
        # Here, we're creating a new tuple that includes the fields from UserSchema plus "email" and "security_answer". This is done to adhered to D.R.Y
        fields = UserSchema.Meta.fields + ("email", "security_answer")

class BasePasswordSchema(BaseSchema):
    new_password = fields.Str(required=True)
    confirm_password = fields.Str(required=True)

    class Meta:
        unknown = INCLUDE
        fields = ("new_password", "confirm_password")

class ForgetPasswordSchema(BasePasswordSchema):
    username = fields.Str(required=True)
    security_answer = fields.Str(required=True)

    class Meta:
        unknown = INCLUDE
        fields = BasePasswordSchema.Meta.fields + ("username", "security_answer")
    
class ResetPasswordSchema(BasePasswordSchema):
    old_password = fields.Str(required=True)

    class Meta:
        unknown = INCLUDE
        fields = BasePasswordSchema.Meta.fields + ("old_password",)
    
class SecurityAnswerSchema(BaseSchema):
    old_security_answer = fields.Str(required=True)
    new_security_answer = fields.Str(required=True)
    confirm_security_answer = fields.Str(required=True)

    class Meta:
        unknown = INCLUDE
        fields = ("old_security_answer", "new_security_answer", "confirm_security_answer")
    