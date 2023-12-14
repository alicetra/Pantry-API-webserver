from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta
from models.user import User
from models.authorization import RegisterSchema, LoginSchema, RevokedToken,ForgetPasswordSchema,ResetPasswordSchema,SecurityAnswerSchema
from utils import validate_data, check_field, prepare_data_dict, validate_fields, create_response, get_model_by_field, check_match
from setup import db
from jwt_config import get_current_user

# 'url_prefix' is a path to prepend to all URLs associated with the Blueprint.
# In this case, all routes defined on the 'users_bp' Blueprint will have '/users' prepended to them. Adhering to D.R.Y 
users_bp = Blueprint('users', __name__, url_prefix='/users')

# This function processes a data dictionary and normalizes all field values to lowercase,
# except for the password fields as for security reason you want that to be case_sensitive_fields.
# This is to provide consistency in the input format of the database and remove duplication.
# Refractoring this in a function ensures consistent application of rules, simplifies code maintenance, and enhances readability
def process_and_normalize_data(data, fields):
    case_sensitive_fields = ['password', 'old_password', 'new_password', 'confirm_password']
    return {field: data[field] if field in case_sensitive_fields else data[field].lower() for field in fields}

@users_bp.route("/register", methods=["POST"])
def register():
    # Create a new instance of the RegisterSchema. The schema is used to validate the incoming request data against.
    schema = RegisterSchema()
    # Validate the incoming request data against the schema. The 'request' object is a global Flask object that holds the current HTTP request data. 
    #This step check that all required fields have been provided, required fields only. It checks that the data type is correct too.
    data = validate_data(request, schema)
    # If the data is a tuple, it means that validation failed and relevant error message will be immediately return based on the schema error handling and requirement.
    if isinstance(data, tuple): 
        return data

    # Get the keys of the schema fields once everything has been validated and we ensured that the correct keys and data types have been provided.
    fields = schema.fields.keys()
    # Process and normalize the data. This function converts all field values to lowercase, except for certain fields like passwords.
    processed_data = process_and_normalize_data(data, fields)

    # Check if the username already exists in the database. If it does, return an error response and the rest of the code will not be executed.
    response = check_field(User, 'username', processed_data['username'], 'Username already taken. Please note that username are case-insentitive')
    if response:
        return response

    # Check if the email already exists in the database. If it does, return an error response and the rest of the code will not be executed.
    response = check_field(User, 'email', processed_data['email'], 'Email already taken')
    if response:
        return response

    # Prepare the keys into data dictionary for validation against staticmethod.
    data_dict = prepare_data_dict(data, fields, User)

    # Validate the fields of the new User instance. If any field is invalid, return an error response and the rest of the code will not be executed.
    #This will check if provided input pass our requirements in our staticmethod such as password requirements ect...
    response = validate_fields(data_dict)
    if response:
        return response

    # Create a new User instance with the processed data and validated data. Harcoding the security question, meaning all users will have the same security question.
    user = User(username=processed_data['username'], email=processed_data['email'], security_question="What is your favourite childhood book")
  
    # Set the password and security answer for the user.
    user.set_password(processed_data['password'])
    user.set_security_answer(processed_data['security_answer'])

    # Add the new User instance to the database session. This stages the user for insertion into the database.
    db.session.add(user)
    # Commit the database session. This inserts the user into the database.
    db.session.commit()
    # Return a success response.
    return create_response('User registered successfully', 201, user={'username': processed_data['username'], 'email': processed_data['email']})


@users_bp.route("/login", methods=['POST'])
def login():
    schema = LoginSchema()
    data = validate_data(request, schema)
    if isinstance(data, tuple): 
        return data

    fields = schema.fields.keys()
    processed_data = process_and_normalize_data(data, fields)

    # it's retrieving a 'User' object where the 'username' field matches  the processed input field username
    user = get_model_by_field(User,'username', processed_data['username'])

    # Check if the user exists and if the password is correct. If not,  immediately return an error response with the message 'Invalid username or password' and rest of our code will not be executed. 
    response = check_match(user and user.check_password(processed_data['password']), True, 'Invalid username or password')
    if response:
        return response

    # This line is creating a timedelta object that represents a duration of time. In this case, it’s being set to a duration of 1 hour
    expires = timedelta(hours=1)
    # This line is creating an access token for the user as a login is successful. The expires_delta argument is being set to the expires timedelta object created earlier.
    # This means the token will expire 1 hour after being issued.
    access_token = create_access_token(identity=user.id, expires_delta=expires)
    response, status_code = create_response(f'Login successful with {processed_data["username"]}', 200, access_token=access_token)
    # This line is adding the access token to the Authorization header in the response. 
    # Even though in the above line I already return the token in the response body it is common practice to also return it in the Authorization header.
    response.headers['Authorization'] = f'Bearer {access_token}'
    return response, 200

@users_bp.route('/logout', methods=['POST'])
#This is a jwt required route since you  shouldn't be able to can't log out if you aren't log in.
@jwt_required()
def logout():
    # Get the JTI for the current token
    jti = get_jwt()["jti"]  
    # Create a new RevokedToken object with the JTI of the current token
    revoked_token = RevokedToken(jti=jti)
    # Add the revoked token to the database so that once user log out, they cannot access protected routes with their revoked token.
    revoked_token.add()
    # Get the username of the current JTI
    username = get_jwt_identity()
    if username:
        return create_response(f'User {username} logged out successfully', 200)


@users_bp.route("/forget_password", methods=['POST'])
# This is not a jwt required route as if you forgot your password, you logically can't log in. 
# This is the provided option to access your account if that is the case.
def forget_password():
    schema = ForgetPasswordSchema()
    data = validate_data(request, schema)
    if isinstance(data, tuple): 
        return data

    fields = schema.fields.keys()
    processed_data = process_and_normalize_data(data, fields)

    user = get_model_by_field(User,'username', processed_data['username'])

    # Check if the user object is None or if the user's security answer doesn't match the processed data's security answer. 
    #Having the option to verified that this your account through a security answer if you forgot your password is a widely used standard.
    if user is None or not user.check_security_answer(processed_data['security_answer']):
        # If either condition is true, imediatelly return a response with a message 'Invalid username or security answer' and a 401 status code, 
        # This stops the execution of the rest of the code, effectively preventing the the reset of password due to failed identity verification.
        return create_response('Invalid username or security answer', 401)

    #Note that I am doing the staticmethod validations after the code is making sure that user exist and have sucessfully provided their security answer.
    #If they can not identify themselves there is no point to validate new_password for the requirements of a password
    # prior to that stage since they won't be able to change their password. This avoid unecessary computations.
    data_dict = prepare_data_dict(processed_data, fields, User)
    
    response = validate_fields(data_dict)
    if response:
        return response

    # Check if the new password matches the confirm password
    response = check_match(processed_data['new_password'], processed_data['confirm_password'], 'New password and confirm password do not match')
    # If they don't match, imediatelly return a response indicating the mismatch.
    # The rest of the code won't be executed.
    if response:
        return response

    # Check if the new password is different from the existing password
    response = check_match(user.check_password(processed_data['new_password']), False, 'New password must be different from the existing password')
    # If the new password is the same as the existing password, imediatelly return a response indicating that the new password must be different.
    # The rest of the code won't be executed.
    if response:
        return response

    #if it passed all the checks and we are executed this code. It means that user can sucessfully reset their password. 
    # Set the user's password to the new password
    user.set_password(processed_data['new_password'])  
    # Commit the changes to the database
    db.session.commit()  
    # Return a response indicating that the password reset was successful
    return create_response('Password reset successfully', 200)

@users_bp.route("/reset_password", methods=['POST'])
#This a jwt required route, alike above route this is for changing your password when you are login.
#This is not when you forgot your password but just want to change it. This a common route per industry standard.
@jwt_required()
def reset_password():
    schema = ResetPasswordSchema()
    data = validate_data(request, schema)
    if isinstance(data, tuple): 
        return data

    # This line retrieves the current user object.
    user = get_current_user()

    fields = schema.fields.keys()
    # You might ask yourself why we need to normalised the data and converts all field values to lowercase if all password fields are case insentive,
    # its because user is a required field and that field is case-insentive.
    processed_data = process_and_normalize_data(data, fields)

    # Check if the old password provided by the user matches the existing password. This is to add that extra layer of identification before changing a password.
    # This step is crucial to prevent unauthorized password changes in scenarios where a user's account is left logged in and unattended (idle). 
    # Without this check, anyone with access to an idle session could change the password, potentially compromising the account's security.
    response = check_match(user.check_password(processed_data['old_password']), True, 'Invalid old password')
    # If the old password is invalid, immediately return a response indicating the mismatch.
    # This stops the execution of the rest of the code, effectively preventing the the reset of  password due to failed identity verification.
    if response:
        return response

    data_dict = prepare_data_dict(data, fields, User)

    response = validate_fields(data_dict)
    if response:
        return response

    # Check if the new password matches the confirm password.
    response = check_match(processed_data['new_password'], processed_data['confirm_password'], 'New password and confirm password do not match')
    # If they don't match, immediately return a response indicating the mismatch.
    # The rest of the code won't be executed.
    if response:
        return response

    # Check if the new password is different from the old password
    response = check_match(user.check_password(processed_data['new_password']), False, 'New password must be different from old password')
    # If the new password is the same as the old password, immediately return a response indicating that the new password must be different.
    # The rest of the code won't be executed.
    if response:
        return response

    user.set_password(processed_data['new_password'])
    db.session.commit()
    return create_response('Password reset successfully', 200)

@users_bp.route("/reset_security_answer", methods=['POST'])
##This a jwt required route, this is for changing your security answer when you are login.
# This a common option route per industry standard. It's important to provide user an option to change their identification details.
@jwt_required()
def reset_security_answer():
    schema = SecurityAnswerSchema()
    data = validate_data(request, schema)
    if isinstance(data, tuple): 
        return data

    user = get_current_user()

    fields = schema.fields.keys()
    processed_data = process_and_normalize_data(data, fields)

    # Check if the old security answer provided by the user matches the existing security answer. 
    # This step is crucial to prevent unauthorized  security answer changes in scenarios where a user's account is left logged in and unattended (idle). 
    # Without this check, anyone with access to an idle session could change the password, potentially compromising the account's security.
    response = check_match(user.check_security_answer(processed_data['old_security_answer']), True, 'Invalid old security answer')
    # If the old security answer is invalid (i.e., it does not match the existing security answer), the function immediately returns a response indicating the mismatch.
    # This stops the execution of the rest of the code, effectively preventing the security answer change due to failed identity verification.
    if response:
        return response

    data_dict = prepare_data_dict(processed_data, fields, User)

    response = validate_fields(data_dict)
    if response:
        return response

    # Check if the new security answer matches the confirm security answer.
    response = check_match(processed_data['new_security_answer'], processed_data['confirm_security_answer'], 'New security answer and confirm security answer do not match')
    # If they don't match, immediately return a response indicating the mismatch.
    # The rest of the code won't be executed.
    if response:
        return response

    # Check if the new security answer is different from the old security answer.
    response = check_match(user.check_security_answer(processed_data['new_security_answer']), False, 'New security answer must be different from old security answer. Please note that security answer are case-insentive')
    # If the new security answer is the same as the old security answer, immediately return a response indicating that the new security answer must be different.
    # The rest of the code won't be executed.
    if response:
        return response

    user.set_security_answer(processed_data['new_security_answer'])
    db.session.commit()
    return create_response('Security answer reset successfully', 200)