from flask import jsonify, request
from marshmallow import Schema, fields, ValidationError
from models.user import User
from models.pantry import PantryItem 
import json

def check_duplicate_keys(pairs):
    keys = [key for key, value in pairs]
    # if the length of the list of keys is not equal to the length of the set of keys, it means there are duplicates
    if len(keys) != len(set(keys)):
        # If there are duplicate keys, return an error message as a JSON response
        # The status code 400 indicates a 'Bad Request' error
        return jsonify({"error": "You have put some fields twice in your json file. Data could not be registered."}), 400
        # If there are no duplicate keys, convert the pairs back into a dictionary and return it
    return dict(pairs)


#Initial validation of request data.
def validate_data(request, schema):
    # Get the raw JSON data from the request
    raw_json = request.get_data(as_text=True)

    # Load the JSON data and check for duplicate keys using the 'check_duplicate_keys' function
    # If there are duplicate keys, 'json.loads' will return a tuple with an error message and status code
    result = json.loads(raw_json, object_pairs_hook=check_duplicate_keys)
    if isinstance(result, tuple):  
        return result

    # If there were no duplicate keys, get the JSON data from the request
    data = request.get_json()
    # Validate the data against the provided schema
    errors = schema.validate(data)
    if errors:
        return jsonify(errors), 400
    # If the data is valid, return it
    return data

#Prepares data for my static method validation post initial validation.
def prepare_data_dict(data, fields, model):
    # Define a dictionary that maps fields which are not defined in the model to  their corresponding validation methods
    validation_methods = {
        'new_password': 'password',
        'new_security_answer': 'security_answer',
    }

    # Automatically exclude 'confirm_password' and 'old_password' from validation as they won't need to be validated since new_password and new_security_answer are and they have to match anyway.
    excluded_fields = ['confirm_password', 'old_password','confirm_security_answer','old_security_answer']

    fields = [field for field in fields if field not in excluded_fields]
    data_dict = {}
    for field in fields:
        if field in data:
            # Use the dictionary to determine the validation method
            validation_method = validation_methods.get(field, field)
            value = data[field].lower() if isinstance(data[field], str) and field not in ['new_password', 'confirm_password', 'password'] else data[field]
            data_dict[field] = (getattr(model, f"validate_{validation_method}"), value)
    return data_dict

#Performs the static method validation on prepared data.
def validate_fields(data_dict):
    # Iterate over each item in the data dictionary
    for field_name, field_value in data_dict.items():
        # Unpack the value into a validation function and the data to be validated
        validation_func, field_data = field_value
        try:
            # Try to validate the data using the validation function
            validation_func(field_data)
        except ValidationError as e:
            # If the validation function raises a ValidationError, return an error message
            # The error message includes the name of the field and the error message from the exception
            return jsonify({'error': f"{field_name}: {str(e)}"}), 400



#refractor the format of return responses in my routes since they all have to be consistently json.
def create_response(message, status_code, **kwargs):
    response = {'message': message}
    response.update(kwargs)
    return jsonify(response), status_code

# Checks if two values match. If they don't, returns an error message.
def check_match(value1, value2, error_message):
    if value1 != value2:
        return jsonify({'error': error_message}), 400
    else:
        return None

#Checks if two values are the same. If they are, returns an error message.
def check_no_change(value1, value2, error_message):
    if value1 == value2:
        return jsonify({'error': error_message}), 400
    else:
        return None

# This function checks if a specific field in the User model already has a certain value.
def check_field(User, field, value, error_message):
    # Retrieve a user where the specified field has the specified value
    user_with_same_field = get_model_by_field(User, field, value)
    # Check if such a user exists. If it does, return an error response.
    response = check_match(user_with_same_field, None, error_message)
    if response:
        return response

#Retrieves a model object based on a specific field value. 
def get_model_by_field(Model, field, value):
    return Model.query.filter_by(**{field: value}).scalar()

