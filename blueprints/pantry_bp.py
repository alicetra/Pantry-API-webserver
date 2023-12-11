from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime
from jwt_config import get_current_user
from models.pantry import PantryItem, PantryItemSchema
from utils import validate_data, validate_fields, check_match, prepare_data_dict, create_response
from setup import db

pantry_bp = Blueprint('pantry', __name__, url_prefix='/pantry')

# This function takes an item as input and converts it to lowercase. This ensure consistency in the database,I wanted item to be case-insensitive.
# Refactoring normalize_item to be the single source of item normalization ensures consistent application of rules, simplifies code maintenance, and enhances readability.
def normalize_item(item):
    return item.lower()

# pantry_item.__dict__ is a function that returns a dictionary containing the attributes of the pantry_item (model) as keys and their corresponding values.
#The dictionary comprehension then iterates over these key-value pairs.
# It excludes attributes that start with '_', 'pantry', 'item_id', and 'pantry_id'.
# This function helps to return the data that you wish in the routes while adhering to DRY.
# the reason why I excluded certain key is that I wanted my return to be relevant to the user.
def pantry_item_to_dict(pantry_item):
    return {key: value for key, value in pantry_item.__dict__.items() if not key.startswith('_') and key != 'pantry' and key != 'item_id' and key != 'pantry_id'}

#This function converts the 'used_by_date' attribute of an item into a date object.
def convert_used_by_date_to_date(item):
    item_date = datetime.strptime(item.used_by_date, "%d-%m-%Y").date() 
    return item_date

@pantry_bp.route("/", methods=["GET"])
# This route is JWT required one since user can only access their own pantry
@jwt_required()
def get_pantry():
    #This line retrieves the current user object.
    user = get_current_user()
    # This line retrieves the items in the user's pantry. 
    # The relationship between the `Pantry` and `PantryItem` models allows us to directly access the items in a user's pantry using the `items` attribute.
    pantry_items = user.pantry.items 
    # This line checks if there are any items in the pantry.
    if pantry_items:
        # If there are items, it returns a 200 status code (indicating success) and a list of the items in dictionary form. 
        # The `pantry_item_to_dict` function leverages the relationship between the `Pantry` and `PantryItem` models to convert each item into a dictionary.
        return create_response([pantry_item_to_dict(item) for item in pantry_items], 200)
    # If there are no items in the pantry.
    else:
        # it returns a 200 status code and a message indicating that the pantry is empty. The route is still sucessfull hence the 200 status. 
        # It just returns an empty pantry which is correct.
        return create_response("Pantry is currently empty", 200)

@pantry_bp.route("/<item>", methods=["GET"])
# This route is Jwt required one since user can only access their own pantry
@jwt_required()
def get_pantry_item(item):
    user = get_current_user()
    # This converting the input item from the route @pantry_bp.route("/<item>") to lowercase. 
    # This is done to ensure that the item names are treated in a case-insensitive manner. Since all item in our pantry are saved in a case-insentive manner
    # I wanted the retrieval to be case-insentitive too.
    normalized_item = normalize_item(item)
    pantry_items = user.pantry.items  
     # This line searches for the item in the user's pantry. If the item is found, it is returned. Otherwise, `None` is returned.
    pantry_item = next((item for item in pantry_items if item.item == normalized_item), None)
    # If pantry_item is not none
    if pantry_item:
        # It returns a 200 status code (indicating success) and the item details in dictionary form.
        return create_response(pantry_item_to_dict(pantry_item), 200)
    # If pantry_item did return none 
    else:
        # It returns a 404 status code (indicating that the requested resource could not be found) and a message indicating that the item does not exist in the user's pantry.
        return create_response("Item doesn't exist in your pantry", 404)
        
@pantry_bp.route("/item", methods=["POST"])
# This route is a jwt required one since I only want user to create their own pantry item and no one else.
@jwt_required()
def post_pantry_item():
    # Create a new instance of the PantryItemSchema. The schema is used to validate the incoming request data against.
    schema = PantryItemSchema()
    # Validate the incoming request data against the schema. The 'request' object is a global Flask object that holds the current HTTP request data. 
    #This step check that all required fields have been provided, required fields only. It checks that the data type is correct too.
    data = validate_data(request, schema)
    # If the data is a tuple, it means that validation failed and relevant error message will be immediately return based on the schema error handling and requirement.
    if isinstance(data, tuple): 
        return data

    user = get_current_user()
    pantry = user.pantry  # Get the Pantry associated with the current User

    # Get the keys of the schema fields once everything has been validated and we ensured that the correct keys and data types have been provided.
    fields = schema.fields.keys()
    # Prepare the keys into data dictionary for validation against staticmethod.
    data_dict = prepare_data_dict(data, fields, PantryItem)


    # Validate the fields against the staticmethod. If any field is invalid, return an error response and the rest of the code will not be executed.
    #This will check if provided input pass our requirements in our staticmethod such as count has to be integer ect..
    response = validate_fields(data_dict)
    if response:
        return response

    # if validation is sucessfull, This line normalizes the item name by converting it to lowercase. This ensures consistency in how items are stored and retrieved.
    item = normalize_item(data['item'])
    # This line replaces the original inputed item name which may be case-sensitive with the normalized item name which is now lowercase.
    data['item'] = item  

    # # This line retrieves the items in the user's pantry
    # The relationship between the `Pantry` and `PantryItem` models allows us to directly access the items in a user's pantry using the `items` attribute.
    existing_items = pantry.items
     # This line checks if the item already exists in the pantry. If it does, a response containing an error message is immediately returned and the rest of the code will not be executed.
    response = check_match(any(existing_item.item == item for existing_item in existing_items), False, "Item already exists in the pantry. Please note that item names are case-insensitive")
    if response:
        return response

    # After passing the check that this is not a duplicate in the database.
    # This line loads the new item data into the schema . This converts the data into a format that can be used to create a new PantryItem object.
    data = schema.load(data)
    # This line creates a new PantryItem object using the loaded data.
    new_item = PantryItem(**data)
    
    # This line checks if the count of the item is 0. If it is
    if data['count'] == 0:
        # the run_out_time of the item is set to the current time.
        new_item.run_out_time = datetime.now()

    # This line adds the new item to the user's pantry. The relationship between the `Pantry` and `PantryItem` models allows us to easily add items to a pantry.
    pantry.items.append(new_item) 
    # This line commits the changes to the database. This saves the new item in the database.
    db.session.commit()
    return create_response("Item added to the pantry", 201)