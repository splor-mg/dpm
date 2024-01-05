import re
from unidecode import unidecode
from frictionless import Schema

def as_identifier(x, case=str.lower): 
    result = unidecode(x) 
    result = re.sub(r'\([^)]*\)', '', result)  # Remove all characters within parentheses
    result = result.replace('\u00a0', ' ')  # Replace non-breaking space with regular space
    result = re.sub('\W|^(?=\d)','_', result)
    result = re.sub('_+', '_', result)
    result = case(result)
    return result.strip('_')

def remove_field_properties(schema, field_name, properties):
    schema_descriptor = schema.to_descriptor()
    field_descriptor = schema.get_field(field_name).to_descriptor()
    
    for property in properties:
        field_descriptor.pop(property, None)
        
    schema_descriptor['fields'] = [
        field_descriptor if field['name'] == field_name else field 
        for field in schema_descriptor['fields']
    ]

    return Schema.from_descriptor(schema_descriptor)