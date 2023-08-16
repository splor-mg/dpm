import re
from unidecode import unidecode
from frictionless import Schema

def as_identifier(x): 
    x = unidecode(x) 
    ret = re.sub('\W|^(?=\d)','_', x).lower()
    return ret

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