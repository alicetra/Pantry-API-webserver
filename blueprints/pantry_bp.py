from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from datetime import datetime
from jwt_config import get_current_user
from models.pantry import PantryItem, PantryItemSchema, DeletePantryItemSchema, UpdatePantryItemSchema
from utils import validate_data, validate_fields, check_match, prepare_data_dict, create_response, check_no_change
from setup import db
from marshmallow import ValidationError

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
        return create_response([pantry_item_to_dict(item) for item in pantry_items], 200)
    # If there are no items in the pantry.
    else:
        # it returns a 200 status code and a message indicating that the pantry is empty. The route  purpose of displaying the pantry is still sucessfull hence the 200 status. 
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

    # This line adds the new item to the user's pantry. 
    pantry.items.append(new_item) 
    # This line commits the changes to the database. This saves the new item in the database.
    db.session.commit()
    return create_response("Item added to the pantry", 201)


@pantry_bp.route("/item", methods=["DELETE"])
# This route is a jwt required one since I only want the user to be allowed to delete their own pantry item and no one else.
@jwt_required()
def delete_pantry():
    schema = DeletePantryItemSchema()
    data = validate_data(request, schema)
    if isinstance(data, tuple): 
        return data

    user = get_current_user()

    normalized_item = normalize_item(data['item']) 

    pantry = user.pantry 

    # get the item in the pantry that matches the provided item that is normalised now, or None if no such item exists
    # The relationship between the `Pantry` and `PantryItem` models allows us to directly access the items in a user's pantry using the `items` attribute.
    pantry_item = next((item for item in pantry.items if item.item == normalized_item), None)
    # if item exist and a match has been found
    if pantry_item:
        # this line will delete it from the database.
        db.session.delete(pantry_item)
        # This line commits the changes to the database.
        db.session.commit()
         # This line returns a response indicating that the item has been deleted, along with a 200 status code.
        return create_response(f"{normalized_item} has been deleted", 200)
    # else if item return none meaning item doesnt exist
    # this line returns a response indicating that the item does not exist in the database.
    # the 400 status code is returned when the item does not exist in the database, 
    # which could be considered as an invalid user input - the user is trying to delete an item that doesn’t exist.
    # returning a 400 status code makes it clear that the requested operation of this route (which is for deleting an item) has failed.
    else:
        return create_response(f"{normalized_item} doesn't exist in the database", 400)

@pantry_bp.route("/item", methods=["PUT"])
# This route is a jwt required one since I only want the user to be allowed to ammend the data of their items.
@jwt_required()
def update_pantry():
    schema = UpdatePantryItemSchema()
    data = validate_data(request, schema)
    if isinstance(data, tuple): 
        return data

    user = get_current_user()

    normalized_item = normalize_item(data['item']) 

    pantry = user.pantry  

    pantry_item = next((item for item in pantry.items if item.item == normalized_item), None)

    # This line sets the variable 'updated' to False as an initial state.
    # This variable is used to track whether any actual update operation has been performed on the pantry item.
    # If either 'count' or 'used_by_date' (or both) are not provided in the request data, 
    # the pantry item will not be updated even though the item name (which is the only required field in the schema) is provided.
    # In such a case, we don't want the API to incorrectly indicate that an update operation has been performed.
    # Therefore, we initialize 'updated' to False and only set it to True when we actually update a field of the pantry item.
    updated = False

    # This line checks if pantry_item is None. If it is, it means that no item matching the normalized_item was found in the pantry.
    if pantry_item is None:
        # This line returns a response indicating that the item doesn't exist in the database, along with a 400 status code.
        # The return statement immediately ends the function execution, and the rest of the code will not be executed.
        return create_response(f"{normalized_item} doesn't exist in the database", 400)

    # Note that I am doing the staticmethod validations after the code check that the item exist in the database first.
    # If the item doesn't exist, there will be no update and therefore a validation is not required of the new data.
    # This avoid unecessary computations.
    fields = schema.fields.keys()
    data_dict = prepare_data_dict(data, fields, PantryItem)

    response = validate_fields(data_dict)
    if response:
        return response

    # This line checks if 'used_by_date' is a key in the request (inputted) data.
    if 'used_by_date' in data:
         # this line calls the check_no_change function to see if the new used_by_date is different from the current one.
         # If they are the same, check_no_change will return a response indicating that no update is needed, and this response will be immediately returned to the client and 
         # the rest of the code will not be executed.
        response = check_no_change(pantry_item.used_by_date, data['used_by_date'], f"{normalized_item} could not update used_by_date because the data is the same")
        if response:
            return response
        # If the used_by_date in the request data is different from the current one, this line updates the pantry item's used_by_date with the new date.
        pantry_item.used_by_date = data['used_by_date']
        # Since an update has been made, this line sets 'updated' to True.
        updated = True

    # This line checks if 'count' is a key in the request (inputted) data.    
    if 'count' in data:
        # If 'count' is in the data, this line calls the check_no_change function to see if the new count is different from the current one.
        # If they are the same, check_no_change will return a response indicating that no update is needed, and this response will be immediately returned to the client and 
        # the rest of the code will not be executed.
        response = check_no_change(pantry_item.count, data['count'], f"{normalized_item} could not update count because the data is the same")
        if response:
            return response
        
        #checks if the pantry was empty in the current databased and is now being restocked through the user input. 
        if pantry_item.count == 0 and data['count'] > 0:
            #If so then reset the pantry_item.run_out_time
            pantry_item.run_out_time = None
    
        # This line updates the pantry item's count with the new count from the request data.
        pantry_item.count = data['count']

        # if the new inputted count is 0,meaning we have ran out of stock of this item
        if pantry_item.count == 0:
            # this line sets the pantry_item's run_out_time to the current time. 
            pantry_item.run_out_time = datetime.now()
        # Since an update has been made, this line sets 'updated' to True.
        updated = True

    # if update has been set to True at any point in the code 
    if updated is True:
        # Commit all the change(s)
        db.session.commit()
        return create_response(f"{normalized_item} has been updated", 200)
    else:
        return create_response("No update since no amendment has been provided for either count or used_by_date or both", 400)


@pantry_bp.route("/itemrunout", methods=["GET"])
# This route is a jwt required one since I only want the user to be allowed to grab the items in their pantry that have ran out of stock.
@jwt_required()
def get_runout_items():
    user = get_current_user()
    # This line uses a list comprehension to create a list of pantry items where the count is 0, indicating that they are out of stock.
    runout_items = [item for item in user.pantry.items if item.count == 0]
    # This line checks if the runout_items list is not empty, which means there are out of stock items.
    if runout_items:
            # If there are out of stock items, this line returns a response with
            # a list of these items, each in their dictionary format, along with a 200 status code..
        return create_response([pantry_item_to_dict(item) for item in runout_items], 200)
        # If there are no out of stock items (i.e., the runout_items list is empty), 
        # this line returns a response indicating that there are no out of stock items, along with a 200 status code.
    else:
        return create_response("You have no out of stock items", 200)