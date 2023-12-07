from marshmallow import Schema, ValidationError, validates_schema
from setup import ma


class BaseSchema(ma.Schema):

    # This method is decorated with @validates_schema, meaning it's a custom validation method that gets called when Schema.load() or Schema.validate() is used.
    # It checks if there are any unknown fields in the data being validated. If there are, it raises a ValidationError.
    # This is useful for ensuring that the data doesn't contain any unexpected fields.
    @validates_schema
    # The **kwargs in the method signature is used to capture any additional keyword arguments that are passed to the method.
    # By including **kwargs in the method signature, we're telling Python to capture all additional keyword arguments, even if they're not explicitly listed in the method signature.
    # This can is necessary to prevent TypeErrors when an unexpected keyword argument is passed to the method
    def validate_unknown_fields(self, data, **kwargs):
        unknown = set(data) - set(self.fields)
        if unknown:
            raise ValidationError(f'Only required fields {tuple(self.fields.keys())} are allowed')

    # This method is also decorated with @validates_schema and is another custom validation method.
    # It checks if any of the fields in the data are empty or contain only spaces. 
    @validates_schema
    def validate_empty_fields(self, data, **kwargs):
        for field_name in self.fields.keys():
            field_value = data.get(field_name)
            if field_value is not None and (field_value == "" or str(field_value).isspace()):
                raise ValidationError(f"{field_name} cannot be empty or contain only spaces.", field_name)
    