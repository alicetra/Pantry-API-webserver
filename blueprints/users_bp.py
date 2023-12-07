from flask import Blueprint, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import timedelta
from models.user import User
from models.authorization import RegisterSchema, LoginSchema, RevokedToken
from utils import validate_data, check_field, prepare_data_dict, validate_fields, create_response, get_model_by_field, check_match
from setup import app, bcrypt, db


# 'url_prefix' is a path to prepend to all URLs associated with the Blueprint.
# In this case, all routes defined on the 'users_bp' Blueprint will have '/users' prepended to them. Adhering to D.R.Y 
users_bp = Blueprint('users', __name__, url_prefix='/users')

# This function processes a data dictionary and normalizes all field values to lowercase,
# except for the password fields as for security reason you want that to be case_sensitive_fields.
# This is to provide consistency in the input format of the database and remove duplication.
def process_and_normalize_data(data, fields):
    case_sensitive_fields = ['password', 'old_password', 'new_password', 'confirm_password']
    return {field: data[field] if field in case_sensitive_fields else data[field].lower() for field in fields}

@users_bp.route("/register", methods=["POST"])
def register():
    # Create a new instance of the RegisterSchema. The schema is used to validate the incoming request data against.
    schema = RegisterSchema()
    # Validate the incoming request data against the schema. The 'request' object is a global Flask object that holds the current HTTP request data.
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
    #This will check if provided input pass our requirements in our staticmethod such as password requirements.
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
@jwt_required()
def logout():
    # Get the JTI for the current token
    jti = get_jwt()["jti"]  
    # Create a new RevokedToken object with the JTI of the current token
    revoked_token = RevokedToken(jti=jti)
    #  Add the revoked token to the database so that once user log out, they cannot access protected routes with their revoked token.
    revoked_token.add()
    username = get_jwt_identity()
    if username:
        return create_response(f'User {username} logged out successfully', 200)

