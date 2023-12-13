from flask_jwt_extended import JWTManager, get_jwt_identity
from models.authorization import RevokedToken
from utils import create_response
from models.user import User 

jwt = JWTManager()

# This function is a callback for the Flask-JWT-Extended library.
# It's decorated with 'jwt.token_in_blocklist_loader', which means it's used to check if a JWT token is in a blocklist (or "blacklist").
# If my route have the @jwt_required() decorator it will automatically call the function decorated with @jwt.token_in_blocklist_loader to check if the token is in the blacklist.
# So I dont have to explicitly call the token_in_blocklist loader above my route as long as I got @jwt_required()
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return RevokedToken.is_jti_blacklisted(jti)

@jwt.revoked_token_loader
def revoked_token_callback(jwt_header, jwt_payload):
    return create_response('Token has been revoked. New log in is required to access route purpose', 401)
    
@jwt.expired_token_loader
def handle_expired_token_callback(expired_token, payload):
    return create_response('The token has expired. New log in is required to access route purpose', 401)

@jwt.invalid_token_loader
def handle_invalid_token_callback(error):
    return create_response('Invalid token. Please log in again.', 401)

@jwt.unauthorized_loader
def handle_missing_token_callback(error):
    return create_response('No user is currently logged in. Please input token in bearer header', 401)

# This function retrieves the current user based on the JWT token in the request.
def get_current_user():
     # 'get_jwt_identity()' is a function provided by Flask-JWT-Extended that extracts the identity of the current user from the JWT token.
    current_user_id = get_jwt_identity()
    # 'User.query.get(current_user_id)' is a SQLAlchemy query that retrieves a User object with the specified ID from the database.
    # It returns the User object if it exists, or 'None' if no such user exists.
    return User.query.get(current_user_id)